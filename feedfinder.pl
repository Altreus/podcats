#!/usr/bin/perl

use strict;
use warnings;
use XML::Feed;
use YAML::XS;

my %data = (
    catonmat => 'http://www.catonmat.net/feed',
    substack => 'http://substack.net/rss',
    symkat   => 'http://symkat.com/feed/rss/',
    kentnl   => 'http://blog.fox.geek.nz/feeds/posts/default',
    simcop   => 'http://simcop2387.info/feed/',
    rindolf  => 'http://www.livejournal.com/community/shlomif_hsite/data/rss',
    amix     => 'http://feeds.feedburner.com/amixdk',
    mst      => 'http://www.shadowcat.co.uk/feed/blog/matt-s-trout',
    meeb     => 'http://meeb.org/rss',
);

for (keys %data) {
    my $r;
    $r = XML::Feed->parse(URI->new($data{$_}));

    if ($r) {
        my @e = $r->entries;
        my $e = shift @e;
        $r = {
            url => $e->link,
            title => $e->title,
        };
    }
    else {
        $r = "The feed seems to be down :(";
    }

    $data{$_} = $r;
}

open my $fh, ">", "feeds.yml";

print $fh Dump \%data;

close $fh;
