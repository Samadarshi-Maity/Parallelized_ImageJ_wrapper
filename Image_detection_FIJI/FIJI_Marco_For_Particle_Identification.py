# A function to detect particles in a frame (set).

# ~~~~~~~~~~~ Developed by @ Samadarshi 18.maart.2022. ~~~~~~~~~~~~~~~~~~
#Points to remember:
#1. This function does the following in the same order: 
    # A> enhances contrast
    # B> applies low pass fliter 
    # C> finds the peaks
    # D> Saves the maxima (object detection) in a tsv file. This is presently done in 
    #    a "Temporary" folder, created & deleted during the parallization step
#2. The function has been built to run in parallel.
#3. You can edit the macro to obtain your desired series of processing steps within this function.
#4. This a memory mapped version of the python code. (comfirm the eleimtaion of large RAM dependance)..!
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# Update: there is a problem with the read and write statement in this code... do not improve..it don't ddo what it is supposed to do.
# the garabange dumping still exists. 

def process_NF_particles(path, frame_start, frame_finish, mem_alloc):
    
    '''
    Param:-
    path: the folder which contains the set of images
    frame_start:  the ID of the starting frame (name the frames in 6 digit IDs)
    frame_finish: the ID of the ending frame 
    '''
    
    # import everthing for each process independantly
    import time 
    import numpy as np 
    import pandas as pd
    import os
    import scyjava
    import imagej
    import gc
 
    # total heap memory allocation should not exceed RAM sizes. 
    scyjava.config.add_options(mem_alloc);
    
    # create imageJ instance
    ij = imagej.init('net.imagej:imagej:2.3.0', mode='interactive')
    
    # Set the batch mode to "true" so that the images do not pop up. 
    A_pre = '\nsetBatchMode(true);\nopen("';

    df = pd.DataFrame();
     
    # count the total number fo frames  
    N = frame_finish - frame_start;
    
    # run the timer
    start_time = time.time();
    
    # echo the start of a process
    print("Starting chunk",frame_start,"to",(frame_finish-1));
    
    # define a part of the main macro
    macro_main = '''.tif");
    // ~~~~~~~~~~~~~~~~ modify the macro from here to suit your needs~~~~~~~~~~~~~~
    // Invert the image 
    run("Invert");
    // Enhance the contrast of the image
    run("Enhance Contrast", "saturated=0.35");
    // ~~~~~~~~~Apply the gaussian blur: low pass filter: sigma set at 2~~~~~~~~~~~ 
    run("Gaussian Blur...", "sigma=2");
    // find the peaks after applying the filter 
    run("Find Maxima...", "prominence=7 output=List");
    // ~~~~~~~~~~~~~~~~~~~~~~~~Save the data as a csv file~~~~~~~~~~~~~~~~~~~~~~~~~ 
    '''
    
    # define the temporary saving route 
    basename = '''saveAs("Results", "''';
    ending = '''");\n''';
    filename = "C:/Temporary/Results_"+ str(frame_start)+ "_to_"+ str(frame_finish)+".tsv";
    full_name = basename+filename+ending;
    
    # name the location of the memory mapped array.
    filename_memmap = "C:/Temporary/Array_"+str(frame_start)+ "_to_"+ str(frame_finish)+".array";
    
    # create a memory mapped array
    #Z = np.memmap(filename_memmap, dtype='float32', mode='w+', shape = (1,4));
    new_len = 1;
    
    # loop for a number of frames
    for i in range(frame_start, frame_finish):

        # build a image string 
        n = str(i).zfill(6);

        # find the positions of the particle using the macro
        result = ij.py.run_macro(A_pre+path+n+macro_main+full_name);

        # read the text file into a pandas dataframe
        # dtype drops the precision for more memory ... trade-off
        df = pd.read_csv(filename,dtype = np.float32, sep='\t');

        # add  the frame number to the array
        df['F'] = i*np.ones(len(df.index), dtype=np.float32);
        
        # Develop a code for the memory mapped approach
        
        Z = np.memmap(filename_memmap, dtype='float32', mode='w+', shape = ((new_len),4));
      
        # find the new length of the master array
        master_len = np.shape(Z)[0];
        frame_len = np.shape(df)[0];
        new_len = master_len + frame_len;
        
        # update the size of Z
        Z = np.memmap(filename_memmap, dtype='float32', mode='r+', shape = ((new_len),4));
        
        # dump the df into z
        Z[master_len:,:] = np.array(df);
        
        # print progress status of the process 
        print ("chunk",frame_start,"to", (frame_finish-1),":", round((i-frame_start)/N*100)," percent complete  \r");  
        
        del(Z);
        gc.collect();
    
    # close the Results frames and the "Results" window
    macro_end = '''
      close("Results");
    '''
    result = ij.py.run_macro(macro_end);             
    end_time = time.time();
    print("the time lapse is",(end_time - start_time)/N, "per frame");
    
    
    # remove the imageJ object ... do it or kernel crash can be very severe ......
    del (ij);
    del (df);
    gc.collect();
    
    # return the location of the chunk and the number of rows in the clunk
    return [filename_memmap,new_len]

