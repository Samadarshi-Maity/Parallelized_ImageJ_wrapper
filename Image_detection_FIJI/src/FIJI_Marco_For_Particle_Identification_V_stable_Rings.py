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
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~ Developed by @ Samadarshi 25.juli.2022. ~~~~~~~~~~~~~~~~~~
#1. Chenge the echo technnique from manual to tqdm 

def process_NF_particles(path, frame_start, frame_finish, mem_alloc):
    
    '''
    Param:-
    path: the folder which contains the set of images
    frame_start:  the ID of the starting frame (name the frames in 6 digit IDs)
    frame_finish: the ID of the ending frame 
    '''
    
    # import everthing for each process independantly
    import numpy as np 
    import pandas as pd
    import os
    import scyjava
    import imagej
    import gc
    from tqdm import tqdm
 
    # total heap memory allocation should not exceed RAM sizes. 
    scyjava.config.add_options(mem_alloc);
    
    # create imageJ instance
    ij = imagej.init('net.imagej:imagej:2.3.0', mode='interactive')
    
    # Set the batch mode to "true" so that the images do not pop up. 
    A_pre = '\nsetBatchMode(true);\nopen("';
    Z = pd.DataFrame();
    df = pd.DataFrame();
     
    # count the total number of frames  
    N = frame_finish - frame_start;
    
    # define a part of the main macro
    macro_main = '''.tif");
    // ~~~~~~~~~~~~~~~~ modify the macro from here to suit your needs~~~~~~~~~~~~~~
    // Invert the image 
    run("Invert");
    // Enhance the contrast of the image
    run("Enhance Contrast", "saturated=0.35");
    run("Enhance Contrast", "saturated=0.35");
    run("Enhance Contrast", "saturated=0.35");
    run("Enhance Contrast", "saturated=0.35");
    run("Enhance Contrast", "saturated=0.35");
    run("Enhance Contrast", "saturated=0.35");
    // ~~~~~~~~~Apply the gaussian blur: low pass filter: sigma set at 2~~~~~~~~~~~ 
    run("Gaussian Blur...", "sigma=2");
    // find the peaks after applying the filter 
    run("Find Maxima...", "prominence=10 output=List");
    // ~~~~~~~~~~~~~~~~~~~~~~~~Save the data as a tsv file~~~~~~~~~~~~~~~~~~~~~~~~~ 
    '''
    
    # define the temporary saving route 
    basename = '''saveAs("Results", "''';
    ending = '''");\n''';
    filename = "C:/Temporary/Results_"+ str(frame_start)+ "_to_"+ str(frame_finish)+".tsv";
    full_name = basename+filename+ending;
    
    # loop for a number of frames
    for i in tqdm(range(frame_start, frame_finish)):

        # build a image string 
        n = str(i).zfill(6);

        # find the positions of the particle using the macro
        result = ij.py.run_macro(A_pre+path+n+macro_main+full_name);

        # read the text file into a pandas dataframe
        # dtype drops the precision for more memory ... trade-off
        df = pd.read_csv(filename,dtype = np.float32, sep='\t');

        # add  the frame number to the array
        df['F'] = i*np.ones(len(df.index), dtype=np.float32);
        
        # concatenate with the master array
        Z = pd.concat([Z,df[['X', 'Y', 'F']]]);  

    # ~~~~~~~~~~~ close the Results frames and the "Results" window ~~~~~~~~~~~~
    macro_end = '''
      close("Results");
    '''
    result = ij.py.run_macro(macro_end);             

    # remove the imageJ object ... do it or kernel crash can be very severe ......
    del (ij);
    del (df);
    gc.collect();
    
    return Z


