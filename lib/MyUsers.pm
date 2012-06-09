package MyUsers;

use strict;
use warnings;

my $USERS = {
	     sri => 'unko',
	     };

sub new { bless {}, shift }

sub check {
  my ($self, $user, $pass) = @_;

  return 1 if $USERS->{$user} && $USERS->{$user} eq $pass;

  return;
}

1;

1;
