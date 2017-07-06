


import pyaudio
import struct
import math
import wave
import os





#amplitudes range between +32768 and -32768 
SHORT_NORMALIZE = (1.0/32768.0)
# ##########################################################

#this is the pause which according to my empirical research 
# from ted videos,i found out that a normal speaker pauses before starting a next word normally.
# my plan here is to look for this half pause duration and if they occurs consecutively,i will count
# them as one pause
# more the pause,less fluency the speaker has.
half_pause_duaration=float(0.375)

# ask the user for file name to analyze
file_name=raw_input("Enter File name")
#change this line if you want to save all your files in another folder,currently its my desktop.
file_destination=os.path.join("C:/Users/nones/Desktop/",str(file_name)+".wav")

f=wave.open(file_destination)
framerate=f.getframerate()
channels = f.getnchannels()
frames=f.getnframes()
duration=frames/framerate



print "Duration"+str(duration)
print "Framerate"+str(framerate)
print "Frames"+str(frames)

# copy and pasted from someone else's code.
#gets the root mean square amplitude from each block

def get_rms( block ):
# RMS amplitude is defined as the square root of the 
# mean over time of the square of the amplitude.
# so we need to convert this string of bytes into 
# a string of 16-bit samples...

# we will get one short out for each .
# two chars in the string.

#the avearage of a each block
    count = len(block)/2
    if count==0:
        return
    format = "%dh"%(count) 
    shorts = struct.unpack( format, block )

    # iterate over the block.
    sum_squares = 0.0
    for sample in shorts:
        # sample is a signed short in +/- 32768. 
        # normalize it to 1.0
        n = sample * SHORT_NORMALIZE
        sum_squares += n*n
       

    return math.sqrt( sum_squares / count )

class FluencyTester(object):
    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.stream = self.open_stream()

    def stop(self):
        self.stream.close()

# opens the stream of audio

    def open_stream( self ):
        
        stream = self.pa.open(   format = self.pa.get_format_from_width(f.getsampwidth()),
                                 channels = f.getnchannels(),
                                 rate = f.getframerate(),
                                  output = True,
                              )

        return stream

    

    def listen(self):
        # this is count of pause occured,
        pause_count=0
        # if two pause occurs in succesion then this gets increased and actually
        # counted as a pause
        alternate_pause_count=0
        # counting the number of loops?!!!
        loop_counter=0
        try:
            #get 0.0375 seconds of audio in the block
            block = f.readframes(int(framerate*half_pause_duaration))
            self.stream.write(block)
            raw_input("playing")  
        except IOError, e:
            # dammit. 
            return
        #loop over all the audio in sections of 0.0375 secs
        for audio_sections in range(0,(int(duration/half_pause_duaration))):
            amplitude = get_rms( block )  
            loop_counter=loop_counter+1
            # check the value of rms,we can increase and decrease this value
            # to adjust the pause loudness,for eg in noisy environment
            # we would want to increase it,so that noise is not
            # evaluated as speech.
            if amplitude<0.015:
                pause_count=pause_count+1
                # when this loop is first entered,it just exits the loop because
                # it is the first pause and pause_count>1 is false and it never enters 
                # the loop where pause count resets to zero.
                # however on second time,pause_count>1 is true,so it enters the loop
                # alternate pause_count is increased and pause_count is reset.
                if pause_count>1:
                    alternate_pause_count=alternate_pause_count+1
                    pause_count=0
                    #this picks from the point it left,so the pyaudio library is doing the hard work
                    self.stream.write(block)
                    print "playing"
                    block = f.readframes(int(framerate*half_pause_duaration))
                    amplitude=get_rms(block)

            else:
                self.stream.write(block)
                raw_input ("playing")
                block = f.readframes(int(framerate*half_pause_duaration))
                amplitude=get_rms(block) 
           
        print "alternate pause count:"+str(alternate_pause_count)
        
        #calculate number of pauses in percentage of duration

        fluency_meter=float(alternate_pause_count)/duration    
        total_pause_duration=fluency_meter*half_pause_duaration
        pause_percentage=total_pause_duration/duration

        # try to convert in it whole number
        # the higher the number,better the fluency,its best to practice on same set of text
        # and see how the fluency grows when you make less mistakes and dont fumble.
        try:
            inverse_total_pause_percentage=pause_percentage**-1
        except:
            inverse_total_pause_percentage="Perfect"
        print "Your fluency: "+str(inverse_total_pause_percentage)
        print "Number of pauses you took :"+str(alternate_pause_count)
        print "Duration"+str(duration)
       

                
                
                
           

if __name__ == "__main__":
    tt = FluencyTester()

tt.listen()
