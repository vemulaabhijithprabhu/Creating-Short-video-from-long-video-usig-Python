import os
import cv2
import ffmpeg
from moviepy.editor import VideoFileClip, AudioFileClip

def extract_clips(input_file, output_dir, clip_ranges):
    """Extracts clips from a video based on given time ranges."""
    try:
        os.makedirs(output_dir, exist_ok=True)
        clip = VideoFileClip(input_file)

        for start, end in clip_ranges:
            subclip = clip.subclip(start, end)
            output_file = f"{output_dir}/clip_{start}_{end}.mp4"
            subclip.write_videofile(output_file)
    except Exception as e:
        print(f"Error extracting clips: {e}")

def extract_audio(input_file, output_file):
    """Extracts audio from a video file."""
    try:
        audioclip = AudioFileClip(input_file)
        audioclip.write_audiofile(output_file)
    except Exception as e:
        print(f"Error extracting audio: {e}")

def crop_and_merge_clips(clip_dir, output_video_file, desired_width, desired_height):
    """Crops and merges extracted clips into a final video."""
    try:
        clip_files = [f for f in os.listdir(clip_dir) if f.endswith('.mp4')]
        clip_files.sort()

        # Create a list to store all frames
        all_frames = []

        for clip_file in clip_files:
            cap = cv2.VideoCapture(os.path.join(clip_dir, clip_file))

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Crop and resize the frame as needed
                h, w, _ = frame.shape
                if w / h > desired_width / desired_height:
                    new_height = int(w * desired_height / desired_width)
                    start_y = (h - new_height) // 2
                    end_y = start_y + new_height
                    frame = frame[start_y:end_y, :]
                else:
                    new_width = int(h * desired_width / desired_height)
                    start_x = (w - new_width) // 2
                    end_x = start_x + new_width
                    frame = frame[:, start_x:end_x]

                frame = cv2.resize(frame, (desired_width, desired_height))
                all_frames.append(frame)

            cap.release()

        # Create a video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_video_file, fourcc, 30, (desired_width, desired_height))

        # Write all frames to the output video
        for frame in all_frames:
            out.write(frame)

        out.release()

    except Exception as e:
        print(f"Error cropping and merging clips: {e}")

def create_short_video(input_video, output_file, clip_ranges, desired_width, desired_height, audio_file = None):
    """Creates a short video from the given input video and clip ranges."""
    temp_dir = "temp_clips"
    extract_clips(input_video, temp_dir, clip_ranges)

    # Extract audio if not provided
    if not audio_file:
        audio_file = "temp_audio.mp3"
        extract_audio(input_video, audio_file)

    # Use MoviePy for video merging instead of OpenCV (cleaner)
    crop_and_merge_clips(temp_dir, output_file + ".temp.mp4", desired_width, desired_height)

    # Merge audio using MoviePy (more user-friendly)
    final_clip = VideoFileClip(output_file + ".temp.mp4")
    final_clip = final_clip.set_audio(AudioFileClip(audio_file))
    final_clip.write_videofile(output_file)  # No need for separate FFmpeg call

    # Clean up temporary directory
    try:
        os.rmdir(temp_dir)
        os.remove(output_file + ".temp.mp4")
    except OSError as e:
        print(f"Error deleting temporary files: {e}")

# Example usage with MoviePy for merging
input_video = "New Robot Makes Soldiers Obsolete.mp4"
output_file = "short_video_with_audio.mp4"
clip_ranges = [(3, 5), (14, 18), (23, 24), (125, 128), (130, 140), (191, 199), (39, 45), (166, 174), (204, 215), (220, 225)] # 1 min video 
desired_width = 540
desired_height = 960
audio_file = "robot2audio-.mp3"  # Use audio from input video

create_short_video(input_video, output_file, clip_ranges, desired_width, desired_height, audio_file)
