#!/usr/bin/perl

use strict; 
use warnings;
use Text::Unaccent;
use GD::Graph::linespoints;
use GD::Graph::colour qw(:colours);

my %letters;

while( my $word = <> ) {
    chomp $word;

    $word = unac_string("UTF-8", $word);

    my @letters = split //, $word;

    my $i = 0;
    for( @letters ) {
        my $space = ($i == 0) ? 0 : $i / (@letters - 1);

        $letters{$_}{$space}++;
        $i++;
    }
}

for( keys %letters ) {
    my %data = %{$letters{$_}};

    my $graph = GD::Graph::linespoints->new(300,300);

    $graph->set(
        x_label => "Position",
        y_label => "Frequency",
        title   => "Positional Frequency of '$_'",
        x_labels_vertical => 1,
        x_tick_number => 8,
        x_max_value => 1,
        x_min_value => 0,
        x_long_ticks => 1,
        text_space => 24,
        bgclr => "white",
        fgclr => "lblue",
        box_axis => 0,
        transparent => 0,
    ) or die $graph->error;

    my $gd = $graph->plot([
        [ sort keys %data ],
        [ map { $data{$_} } sort keys %data ]
    ]);

    open my $img, ">", "$_.png";
    print $img $gd->png;
    close $img;
}
