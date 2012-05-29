#!/usr/bin/perl

use strict;
use warnings;

use CGI;

use lib('./lib/');
use Share;

my $query = CGI->new;
print $query->header( -charset => "utf-8", -type => 'text/plain');

Share::share_gomi;
