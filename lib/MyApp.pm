package MyApp;
use Mojo::Base 'Mojolicious';

use MyUsers;

sub startup {
  my $self = shift;

  $self->secret('Mojolicious rocks');
  my $users = MyUsers->new;
  $self->helper(users => sub {return $users });

  my $r = $self->routes;
  $r->any('/')->to('login#index')->name('index');
  $r->get('/protected')->to('login#protected')->name('protected');
  $r->get('/logout')->to('login#logout')->name('logout');
}

1;
