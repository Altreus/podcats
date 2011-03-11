#!/usr/bin/perl

use strict;
use warnings;

use open IN => ':utf8';

use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);
use Carp::Always;
use List::Util;

use Blog::Blosxom::Podcats;

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

my $content_type = {
    html => 'text/html; charset=ISO-8859-1',
    atom => 'application/atom+xml; charset=utf-8',
}->{$flavour} || 'text/html';

print header($content_type),
      $blog->run($path, $flavour);
