#!/usr/bin/perl

use strict;
use warnings;

use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
use Carp::Always;

my $blog = Blog::Blosxom::Podcats->new(
    blog_title => "Podcats",
    blog_description => "And how.",
    blog_language => "en",
    datadir => "/home/altreus/code/podcats.in/docs/blosxom",
    url => "http://testing.podcats.in",
    depth => 0,
    num_entries => 10,
    file_extension => "bxm",
    default_flavour => "html",
    show_future_entries => 0,
    require_namespace => 1,
#    plugin_dir => "/home/al/code/blosxom_plugins",
);

my $path = path_info() || param('path');
my $flavour = param('flav');

$path =~ s/\.(\w+)$// and $flavour = $1;

print header,
      $blog->run($path, $flavour);
      

package Blog::Blosxom::Podcats;

use base qw/Blog::Blosxom/;

use Syntax::Highlight::Engine::Kate::Haskell;
use Syntax::Highlight::Engine::Kate::JavaScript;
use Syntax::Highlight::Engine::Kate::HTML;
use Syntax::Highlight::Engine::Kate::Bash;
use Syntax::Highlight::Engine::Kate::Perl;

use Parse::BBCode;
use HTML::Entities qw(encode_entities);
use Class::C3;
use File::Spec;
use File::Find;
use POSIX;

use YAML::XS;

use Data::Dumper;

sub date_of_post {
    my ($self, $post) = @_;

    my (undef, undef, $fn) = File::Spec->splitpath($post);

    my ($y, $m, $d) = ($fn =~ /(\d{4})-(\d{2})-(\d{2})/);

    return POSIX::mktime(0,0,0,$d,$m-1,$y-1900) || $self->next::method($post);
}

# Override how we match a single file, or else relinquish control to
# default implementation.
sub entries_for_path {
    my ($self, $path) = @_;

    my (undef, $dir, $fn) = File::Spec->splitpath($path);

    # If this is root, we will accidentally only get one result, so avoid it.
    if ($fn) {
        my $abs_path = File::Spec->catdir($self->{datadir}, $dir);
        my $fex = $self->{file_extension};
        
        my ($match) = grep -f, glob (File::Spec->catdir($abs_path, "*$fn.$fex"));
        $match = File::Spec->abs2rel($match, $self->{datadir});

        return [$match] if $match;
    }
    my @ret = next::method(@_);
}

sub head_data {
    my $self = shift;

    my $data = $self->next::method();
    $data->{date_of_last_entry} 
        = sprintf('%d-%02d-%02dT%02d:%02d:%02d',
            @{$self->{entries}[-1]}{qw(yr mo_num da hr min)}, 0);

    return $data;
}

# Look for meta files and put values in metadata namespace
sub interpolate {
    my ($self, $template, $extra_data) = @_;

    my $path = $self->{path_info};

    my $fn = File::Spec->catfile( $self->{datadir}, $path, "meta" );

    my %metadata;

    while (1) {
        my %local_data;

        # Return the contents of this template if the file exists. If it is empty,
        # we have defaults set up.
        if (-e $fn) {
            open my $fh, "<", $fn;
            while (<$fh>) {
                chomp;
                my ($var, $val) = split /:\s+/, $_, 2;
                $local_data{$var} = $val;
            }
        }

        # This is not the wrong way around. We're going backwards.
        # Existing stuff takes priority.
        %metadata = (%local_data, %metadata);

        # Stop looking when our relative path is root.
        last if !$path or $path eq File::Spec->rootdir;

        # Look one dir higher and go again.
        my @dir = File::Spec->splitdir($path);
        pop @dir;
        $path = File::Spec->catdir(@dir);

        $fn = File::Spec->catfile( $self->{datadir}, $path, "meta" );
    }

    package metadata;

    {
        no strict 'refs';
        while( my ($var, $val) = each %metadata ) {
            ${$var} = $val;
        }
    }

    package main;

    $extra_data->{post_list} = join "\n", map { qq(<li><a href="#post-$_->[1]">$_->[0]</a></li>\n) } @{$self->{post_list}};

    # We've set up our namespace. That should be enough.
    $template = $self->next::method($template, $extra_data);

    return $template;

}

sub entry_data {
    my ($self, $entry) = @_;

    my $entry_data = $self->next::method($entry);

    $entry_data->{post_num} = ++$self->{post_count};
    $entry_data->{fn} =~ s/^\d{4}-\d{2}-\d{2}-//;

    my $tag = $self->is_highlight_flavour ? "pre" : "code";

    my $parse = Parse::BBCode->new({
        tags => {
            Parse::BBCode::HTML->defaults,
            '' => sub {
                my $e = encode_entities($_[2]);

                $e =~ s{\n\n}{</p>\n<p>}g;

                $e;
            },
            c =>  {
                output => '<code>%{html}s</code>',
                block => 0,
                parse => 0,
            },
            code =>  {
                output => '<code>%{html}s</code>',
                block => 0,
                parse => 0,
            },
            h => "<h4>%s</h4>",
            ul => "<ul>%s</ul>",
            li => "<li>%s</li>",
            tldr => {
                code => sub {
                    my ($p, $attr, $content) = @_;

                    qq{<div class="verbose-$attr"><p>$$content</p></div>};
                },
                parse => 1,
            },
            stat    => '%{noparse}s',
            haskell => '<' . $tag . ' class="highlight haskell">%{haskell}s</' . $tag . '>',
            ghci    => '<' . $tag . ' class="highlight haskell">%{haskell}s</' . $tag . '>',
            bash    => '<' . $tag . ' class="highlight sh">%{bash}s</' . $tag . '>',
            shell   => '<' . $tag . ' class="highlight sh">%{shell}s</' . $tag . '>',
            sh      => '<' . $tag . ' class="highlight sh">%{sh}s</' . $tag . '>',
            jquery  => '<' . $tag . ' class="highlight javascript">%{javascript}s</' . $tag . '>',
            html    => '<' . $tag . ' class="highlight html">%{hhtml}s</' . $tag . '>',
            perl    => '<' . $tag . ' class="highlight perl">%{perl}s</' . $tag . '>',
            cpp     => '<' . $tag . ' class="highlight cpp">%{cpp}s</' . $tag . '>',
        },
        escapes => {
            sh => $self->get_highlighter("sh"),
            shell => $self->get_highlighter("sh"),
            bash => $self->get_highlighter("sh"),
            haskell => $self->get_highlighter("haskell"),
            javascript => $self->get_highlighter("javascript"),
            hhtml => $self->get_highlighter("html"),
            perl => $self->get_highlighter("perl"),
            cpp => $self->get_highlighter("cpp"),
            html => sub { return encode_entities($_[2]) },
            noparse => sub { return $_[2] },
        }
    });

    # This is a bit hackish and I might file it as a bug in Parse::BBCode
    #$entry_data->{body} =~ s{<p>\s*</p>}{}gsm;
    $entry_data->{body} = "<p>" . $parse->render($entry_data->{body}) . "</p>";

    push @{$self->{post_list}}, [ $entry_data->{title}, $entry_data->{post_num} ];

    return $entry_data;
}

sub is_highlight_flavour {
    my $self = shift;

    return grep { $self->{flavour} } qw(html)
           > 0;
}

sub get_highlighter {
    my ($self, $lang) = @_;

    my %package = (
        haskell => "Syntax::Highlight::Engine::Kate::Haskell",
        javascript => "Syntax::Highlight::Engine::Kate::JavaScript",
        html => "Syntax::Highlight::Engine::Kate::HTML",
        sh => "Syntax::Highlight::Engine::Kate::Bash",
        perl => "Syntax::Highlight::Engine::Kate::Perl",
        cpp => "Syntax::Highlight::Engine::Kate::Cplusplus",
    );

    return  sub { @_[2] } unless $self->is_highlight_flavour;

    return sub {
        my ($bbparser, $html, $text) = @_;

        ($_ = $package{$lang}) =~ s{::}{/}g;
        require "$_.pm";

        my $h1 = $package{$lang}->new(
            substitutions => {
               "<" => "&lt;",
               ">" => "&gt;",
               "&" => "&amp;",
               "\t" => "    ",
            },
            format_table => {
               Alert => ['<span class="alert">', '</span>'],
               BaseN => ['<span class="basen">', '</span>'],
               BString => ['<span class="bstring">', '</span>'],
               Char => ['<span class="char">', '</span>'],
               Comment => ['<span class="comment">', '</span>'],
               DataType => ['<span class="datatype">', '</span>'],
               DecVal => ['<span class="decval">', '</span>'],
               Error => ['<span class="error">', '</span>'],
               Float => ['<span class="float">', '</span>'],
               Function => ['<span class="function">', '</span>'],
               IString => ['<span class="istring">', '</span>'],
               Keyword => ['<span class="keyword">', '</span>'],
               Normal => ['<span class="normal">', '</span>'],
               Operator => ['<span class="operator">', '</span>'],
               Others => ['<span class="other">', '</span>'],
               RegionMarker => ['<span class="regionmarker">', '</span>'],
               Reserved => ['<span class="reserved">', '</span>'],
               String => ['<span class="string">', '</span>'],
               Variable => ['<span class="variable">', '</span>'],
               Warning => ['<span class="warning">', '</span>'],
            },
        );

        return $h1->highlightText($text);
    };

}

sub sort {
    my $self = shift;

    my @entries = $self->next::method(@_);

    return reverse @entries;
}

sub foot_data {
    my $self = shift;
    
    open my $fh, "<", "../docs/feeds.yml";
    my $data = Load do{ local $/; <$fh>; };
    close $fh;

    for (keys %$data) {
        my $d = $data->{$_};

        $data->{$_} = sprintf '<a href="%s">%s</a>', $d->{url}, $d->{title};
    }

    $data->{f00li5h} = "<span>Silly kit doesn't have a feed yet.</span>";

    return $data;
}
