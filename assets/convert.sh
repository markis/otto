#!/bin/zsh

mkdir -p medium-teams
mkdir -p medium-bw-teams
mkdir -p small-teams
mkdir -p small-bw-teams
mkdir -p xsmall-teams
mkdir -p old-small-teams
mkdir -p old-small-bw-teams
mkdir -p old-small-fade-teams

pushd raw-teams
for f in *.png
do
convert $f -resize 128x128 -gravity center \
  -extent 128x128 -transparent white ../medium-teams/$f
done
popd

montage -background transparent -tile 1x \
  -compress Lossless -geometry +0+0 \
  medium-teams/*.png medium-teams.png

pushd medium-teams
for f in *.png
do
convert $f -grayscale average -transparent white -compress Lossless ../medium-bw-teams/$f
done
popd

montage -background transparent -tile 1x \
  -compress Lossless -geometry +0+0 \
  medium-bw-teams/*.png medium-bw-teams.png

pushd raw-teams
for f in *.png
do
convert $f -resize 64x64 -gravity center \
  -extent 64x64 -transparent white ../small-teams/$f
done
popd

montage -background transparent -tile 1x \
  -compress Lossless -geometry +0+0 \
  small-teams/*.png small-teams.png

pushd small-teams
for f in *.png
do
convert $f -grayscale average -transparent white -compress Lossless ../small-bw-teams/$f
done
popd

montage -background transparent -tile 1x \
  -compress Lossless -geometry +0+0 \
  small-bw-teams/*.png small-bw-teams.png


pushd raw-teams
for f in *.png
do
convert $f -resize 40x40 -gravity center \
  -extent 40x40 -transparent white ../xsmall-teams/$f
done
popd

montage -background transparent -tile 1x \
  -compress Lossless -geometry +0+0 \
  xsmall-teams/*.png xsmall-teams.png

pushd raw-teams
for f in *.png
do
convert $f -resize 15x15 -gravity center \
  -extent 15x15 -transparent white ../old-small-teams/$f
done
popd

montage -background transparent -tile 1x \
  -compress Lossless -geometry +0+0 \
  old-small-teams/*.png old-small-teams.png


pushd old-small-teams
for f in *.png
do
convert $f -fill white -colorize 50% -transparent white -compress Lossless ../old-small-fade-teams/$f
done
popd

montage -background transparent -tile 1x \
  -compress Lossless -geometry +0+0 \
  old-small-fade-teams/*.png old-small-fade-teams.png
