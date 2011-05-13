#!/usr/bin/env perl

use strict;
use warnings;

use open IN => ':utf8';

use Carp::Always;
use List::Util;
use Plack::Request;

use Blog::Blosxom::Podcats;

my $blog = Blog::Blosxom::Podcats->new(
    blog_title => "Podcats",
    blog_description => "And how.",
    blog_language => "en",
    datadir => "/home/al/code/websites/podcats.in/docs/blosxom",
    url => "http://testing.podcats.in",
    depth => 0,
    num_entries => 10,
    file_extension => "bxm",
    default_flavour => "html",
    show_future_entries => 0,
    require_namespace => 1,
#    plugin_dir => "/home/al/code/blosxom_plugins",
);

my $app = sub {
    my $env = shift;
    my $req = Plack::Request->new($env);

    my $path = $req->path_info() || $req->param('path');
    my $flavour = $req->param('flav');

    $path =~ s/\.(\w+)$// and $flavour = $1;

    my $content_type = {
        html => 'text/html; charset=ISO-8859-1',
        atom => 'application/atom+xml; charset=utf-8',
    }->{$flavour} || 'text/html';

    my $res = $req->new_response(200);
    $res->content_type($content_type);
    $res->body( $blog->run( $path, $flavour ));

    return $res->finalize;
};
