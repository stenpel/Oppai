package Share;

use strict;
use warnings;

use CGI;
use CGI::Simple::Cookie;
use CGI::Simple::Standard qw(header);
use URI;
use LWP::UserAgent;
use JSON qw/encode_json decode_json/;

use Data::Dumper;

my $client_id = '4eb3fd2526f637515784';
my $client_secret = 'f024fa3a53ce5350d0eccee6b5036cf7fc7d0105';

sub is_exist_token {
  my %cookies = CGI::Simple::Cookie->fetch;
  return unless %cookies;

  return %cookies;
}

sub get_refresh_token {
  my %cookies = is_exist_token();
  return unless %cookies;

  return $cookies{refresh_token}->value;
}

sub get_access_token {
  my %cookies = is_exist_token();

  return unless %cookies;

  return $cookies{access_token}->value;
}

sub share_gomi {
  my ($access_token) = @_;
  warn $access_token;
  $access_token = $access_token || get_access_token();
  warn $access_token;
  my $json = '{"key":"9e34a52c5be08e8ecc124d7f8fb04442e8c5b013","title":"ちんちんうｐ","primary_url":"http://google.com","pc_url":"http://google.com","privacy":{"visibility":"self"}}';
  my $user_agent = new LWP::UserAgent();
  my $response = $user_agent->post(
				   "http://api.mixi-platform.com/2/share",
				   "Authorization" => "OAuth $access_token",
				   "Content-Type" => "application/json",
				   "Content" => "$json"
				  );
  if($response->is_success){
    print 'OK';
  } else {
    warn Dumper $response;
    my $error_content = $response->content;
    my $error_status = $response->headers->header('www-authenticate') || "";

    if(index($error_status, 'expired_token') > 0) {
      $access_token = get_access_token_by_refresh_token(get_refresh_token());
      warn Dumper $access_token;
      $access_token ? share_gomi($access_token) : 0;
    }
  }
  exit;
}

sub get_access_token_by_refresh_token {
  my ($refresh_token) = @_;
  my $user_agent = new LWP::UserAgent();
  my $response = $user_agent->post(
                                     "https://secure.mixi-platform.com/2/token",
                                     {
                                         "grant_type" => "refresh_token",
                                         "client_id"  => "$client_id",
                                         "client_secret" => "$client_secret",
                                         "refresh_token" => "$refresh_token",
                                     },
                                     "Content-Type" => "application/x-www-form-urlencoded"
                                     );
    if($response->is_success) {
        my $content = decode_json($response->content);

        my $cookie_access_token  = CGI::Simple::Cookie->new( -name => 'access_token', -value => $content->{access_token});
        my $cookie_refresh_token = CGI::Simple::Cookie->new( -name => 'refresh_token', -value => $content->{refresh_token});

        print header( -cookie=>[$cookie_access_token, $cookie_refresh_token] );

        return $content->{access_token};
    }

    else {
        print 'ERROR';
    }
}

1;
