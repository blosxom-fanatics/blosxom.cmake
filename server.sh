#!/bin/sh

plackup -MPlack::App::CGIBin -e 'Plack::App::CGIBin->new(root => ".", exec_cb => sub { 1 })->to_app'

