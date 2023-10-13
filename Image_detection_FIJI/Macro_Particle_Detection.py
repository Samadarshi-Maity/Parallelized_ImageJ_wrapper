from FIJI_Marco_For_Particle_Identification import process_NF_particles as pnp
import glob
import multiprocessing.freeze_support() as mp
import numpy as np 
import os
import pandas as pd
import scipy.io as sio
import shutil
import time 

# parallelization code set
# ~~~~~~~~~~~~~~~~~~"Create  the file architecture 
# add the main path 

mainPath  = 'D:/binary_flock_density_manipulation/density_1.00_date_11.3.2022'; 
# add the last slash as well
experimentPath = glob.glob( os.path.normpath(mainPath)+'\*_files');

# add the Images 
experimentPath = [s + '\\Images\\' for s in experimentPath];
experimentPath = [s .replace('\\','/') for s in experimentPath];

for Path in experimentPath:
    
    # ~~~~~~~~~~~ Count the total number of frames within the "Image" folder ~~~~~~~~~~~~~
    Total_Frames = len(glob.glob(Path +'*.tif'));
    if (os.path.normpath(glob.glob(Path +'*.tif')[-1]).split(os.sep)[-1] == 'ImageBackground.tif'):
        Total_Frames -= 1;
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # ~~~~~~~~~~~~ read the total number of images ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    N  = 8; # specify the number of workers ... do this judiciously  
    Ram_size = 30;
    memory_allocation = "-Xmx" + str(int (Ram_size/N)) + "g"; # N*memory alloc. not exceed the RAM size-1
    pool = mp.Pool(processes=N);
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #~~~~~~~~~~~~~~~~create the chunk firsts and lasts (tested robust) ~~~~~~~~~~~~~~~~~~~
    Chunk = (Total_Frames/N);
    frame_start = [];
    frame_finish =[];
    inp_for_starmap =[];

    for i in range(N):
        frame_start.append(int(np.floor(i*Chunk)+1));
        frame_finish.append(int(np.floor((i+1)*Chunk+1)));
        inp_for_starmap.append(tuple([Path,frame_start[i],frame_finish[i],memory_allocation]));

    #~~~~~~~~~~~~~create a "main" function for running the parallization code~~~~~~~~~~~~~
    #~~~~ the __main__ function is not necessary on mac and linux .. window 's crap!~~~~~~


    if __name__=="__main__":
        
        
        # ~~~~~~~~~~~~~~~~~~~ create a temporary folder in C: Drive ~~~~~~~~~~~~~~~~~~~~~~
        os.mkdir('C:/Temporary')

        start = time.perf_counter();    
        # creating N processes and executing them 
        # using pool which runs serially ... do this once to check whether the workers are being initialised properly
        #results = [pool.apply(pnp, args=(path,frame_start[i-1],frame_finish[i-1],)) for i in range(1,N+1)]

        results = pool.starmap(pnp, inp_for_starmap)

        # combine the data from the pool into a single dataframe ...very important 
        master_array = pd.concat(results);

        # measure the run time
        finish = time.perf_counter();
        print(" time taken by",Path," is ", round((finish - start)/60),"minutes");

        # closing the pool is very important!! creates problem with multiple running 
        pool.close()

        # delete the temprorary folder in C: drive
        shutil.rmtree('C:/Temporary');

        # Transform the path name to the position for saving the .mat output
        parts = os.path.normpath(Path).split(os.sep)[:-1];
        parts.extend(['Analysis','1_Positions','Positions_NF.mat']);
        mat_file_name = '/'.join(parts);

        # Save the data in a .mat file 
        dictn = {"XYZ":np.array(master_array)};
        sio.savemat(mat_file_name, dictn);

        del results;    