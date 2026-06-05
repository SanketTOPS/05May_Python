from pytubefix import YouTube

url="https://www.youtube.com/watch?v=CqA_HAznD6Q"

YouTube(url).streams.first().download()