#!/usr/bin/perl

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
my $redirect_uri = 'http://192.168.25.100/~stenpel/DregsFeedBreeder/index.cgi';
my $q;

run();

sub run {
  init();
}

sub init {
  $q = CGI->new;
  $q->header( -charset => "utf-8");

  share_gomi(get_access_token()) if is_exist_token();

  if($q->param('code')) {
    set_token($q->param('code')) == 1 ? share_gomi() : connect_authorize($q)
  }
  connect_authorize($q);
}

sub get_display_mode {
  my $agent = $ENV{'HTTP_USER_AGENT'};
  if($agent =~ /iPhone/ || $agent =~ /Android/){
    return 'touch';
  } else {
    return 'pc';
  }
}

sub connect_game {
  my $uri = URI->new('http://192.168.25.100/~stenpel/DregsFeedBreeder/');

  print $q->redirect($uri->as_string);
  exit;
}

sub connect_authorize {
  my ($q) = @_;

  my $uri = URI->new('https://mixi.jp/connect_authorize.pl');
  my $params = {
		client_id => "$client_id",
		response_type => "code",
		scope => 'w_share',
		display => get_display_mode(),
	       };
  $uri->query_form(%$params);

  print $q->redirect($uri->as_string);
  exit;
}

sub is_exist_token {
  warn 'is_exist_token';
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
  my $json = '{"key":"9e34a52c5be08e8ecc124d7f8fb04442e8c5b013","title":"20代までに日本で起業するために覚えておくべきたった3つのこと","primary_url":"http://google.com","image":"http://lohas.nicoseiga.jp/thumb/1391060i"}';
  my $user_agent = new LWP::UserAgent();
  my $response = $user_agent->post(
				   "http://api.mixi-platform.com/2/share",
				   "Authorization" => "OAuth $access_token",
				   "Content-Type" => "application/json",
				   "Content" => "$json"
				  );
  if($response->is_success){
    connect_game();
    exit;
  } else {

    my $error_content = $response->content;
    my $error_status = $response->headers->header('www-authenticate') || "";

    if(index($error_status, 'expired_token') > 0) {
      $access_token = get_access_token_by_refresh_token(get_refresh_token());
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
        warn Dumper $response, 'error get_access_token_by_refresh_token';
	connect_authorize();
        return 0;
    }
}

sub set_token {
  my ($code) = @_;
  my $q = CGI->new;
  my $user_agent = new LWP::UserAgent();
  my $response = $user_agent->post(
				   "https://secure.mixi-platform.com/2/token",
				   {
				    "grant_type" => "authorization_code",
				    "client_id"  => "$client_id",
				    "client_secret" => "$client_secret",
				    "code" => "$code",
				    "redirect_uri" => "$redirect_uri",
				   },
				   "Content-Type" => "application/x-www-form-urlencoded"
				  );

  if($response->is_success) {
    my %cookies = CGI::Simple::Cookie->fetch;
    my $content = decode_json($response->content);

    my $access_token = $content->{access_token};

    my $cookie_access_token  = CGI::Simple::Cookie->new( -name => 'access_token', -value => $content->{access_token});
    my $cookie_refresh_token = CGI::Simple::Cookie->new( -name => 'refresh_token', -value => $content->{refresh_token});

    print $q->redirect( -cookie=>[$cookie_access_token, $cookie_refresh_token] );
    warn Dumper $response;
    return 1;
  } else {
    warn Dumper $response;
    return 0;
  }
}

exit;
