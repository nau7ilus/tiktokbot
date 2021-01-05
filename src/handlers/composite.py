from moviepy.editor import VideoFileClip, concatenate_videoclips
from os import listdir

file_names = listdir('output')
clips = list(map(lambda file: VideoFileClip('output/' + file), file_names))
final_clip = concatenate_videoclips(clips)
final_clip.write_videofile("ready.mp4")
