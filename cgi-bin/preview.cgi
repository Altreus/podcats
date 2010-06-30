#!/usr/bin/perl

use strict;
use warnings;

use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);

my $blog = Blog::Blosxom::Podcats->new(
    blog_title => "Podcats",
    blog_description => "And how.",
    blog_language => "en",
    datadir => "/home/al/code/podcats/docs/blosxom",
    url => "http://podcats.localhost",
    depth => 0,
    num_entries => 40,
    file_extension => "bxm",
    default_flavour => "html",
    show_future_entries => 0,
#    plugin_dir => "/home/al/code/blosxom_plugins",
);

my $path = path_info() || param('path');
my ($flavour) = $path =~ s/\.(\w+)$// || param('flav');

print header,
      $blog->run($path, $flavour);
      

package Blog::Blosxom::Podcats;

use base qw/Blog::Blosxom/;

use Class::C3;

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

    no strict 'refs';
    while( my ($var, $val) = each %metadata ) {
        ${$var} = $val;
    }

    # We've set up our namespace. That should be enough.
    $template = $self->next::method($template, $extra_data);

    return $template;

}

