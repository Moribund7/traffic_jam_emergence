cd data/
ffmpeg -framerate 10 -i step%03d.png -c:v libx264 -pix_fmt yuv420p out.mp4
cd ..
mkdir -p  movies
mv data/out.mp4 movies/out.mp4
