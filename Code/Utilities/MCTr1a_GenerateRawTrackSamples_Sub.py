#This simple script prepares 2-segment track seeds for the initial CNN/GNN union
# Part of ANNDEA package
#Made by Filips Fedotovs
#Current version 1.0

########################################    Import libraries    #############################################
import argparse
import pandas as pd #We use Panda for a routine data processing
import math #We use it for data manipulation
import gc  #Helps to clear memory
import numpy as np
import ast




######################################## Set variables  #############################################################
#Setting the parser - this script is usually not run directly, but is used by a Master version Counterpart that passes the required arguments
parser = argparse.ArgumentParser(description='select cut parameters')
parser.add_argument('--i',help="Set number", default='1')
parser.add_argument('--p',help="Path to the output file", default='')
parser.add_argument('--o',help="Path to the output file name", default='')
parser.add_argument('--pfx',help="Path to the output file name", default='')
parser.add_argument('--sfx',help="Path to the output file name", default='')
parser.add_argument('--EOS',help="EOS directory location", default='.')
parser.add_argument('--AFS',help="AFS directory location", default='.')
parser.add_argument('--BatchID',help="Give this training sample batch an ID", default='SHIP_UR_v1')
parser.add_argument('--MaxSegments',help="A maximum number of track combinations that will be used in a particular HTCondor job for this script", default='20000')
parser.add_argument('--ClassHeaders',help="What class headers to use?", default="['EM Background']")
parser.add_argument('--ClassNames',help="What class headers to use?", default="[['Flag','ProcID']]")
parser.add_argument('--ClassValues',help="What class values to use?", default="[['13','-13'],['8']]")


######################################## Set variables  #############################################################
args = parser.parse_args()
i=int(args.i)    #This is just used to name the output file
p=args.p
o=args.o
sfx=args.sfx
pfx=args.pfx
BatchID=args.BatchID
ClassHeaders=ast.literal_eval(args.ClassHeaders)
ClassNames=ast.literal_eval(args.ClassNames)
ClassValues=ast.literal_eval(args.ClassValues)
ExtraColumns=[]
for i in ClassNames:
    for j in i:
        ExtraColumns.append(j)
########################################     Preset framework parameters    #########################################
MaxSegments=int(args.MaxSegments)
#Loading Directory locations
EOS_DIR=args.EOS
AFS_DIR=args.AFS

import UtilityFunctions as UF #This is where we keep routine utility functions

#Specifying the full path to input/output files
input_file_location=EOS_DIR+'/ANNADEA/Data/TRAIN_SET/MCTr1_'+BatchID+'_TRACKS.csv'
output_file_location=EOS_DIR+p+'/'+pfx+'_'+BatchID+'_'+o+'_'+str(i)+sfx
print(UF.TimeStamp(), "Modules Have been imported successfully...")
print(UF.TimeStamp(),'Loading pre-selected data from ',input_file_location)
data=pd.read_csv(input_file_location,header=0,
                    usecols=['x','y','z','tx','ty','Rec_Seg_ID']+ExtraColumns)

track_headers = data[['Rec_Seg_ID']+ExtraColumns]
track_headers = track_headers.drop_duplicates()
track_headers=track_headers.values.tolist()
print(track_headers)
exit()
track_data = data[['x','y','z','tx','ty','Rec_Seg_ID']].values.tolist() #Convirting the result to List data type
print(track_data)
exit()
# tracks = tracks[int(Set)*MaxSegmentsPerJob : min((int(Set)+1)*MaxSegmentsPerJob, len(tracks))]
# gc.collect()
#
# track_counter=0
# print(UF.TimeStamp(),bcolors.OKGREEN+'Data has been successfully loaded and prepared..'+bcolors.ENDC)
# #create seeds
# GoodTracks=[]
# print(UF.TimeStamp(),'Beginning the image generation part...')
# limit = len(tracks)
#
# for s in range(0,limit):
#     track=tracks.pop(0)
#
#
#     #label=(track[1] in MotherPDGList)
#     # for test
#     #print(track[0], track[1], label)
#
#
#     # 0 for incoming muons, 1 for photons and muons, 2 for others
#     if track[1] == 0:
#         label = 0
#     elif track[1] in MotherPDGList:
#         label = 1
#     else :
#         label = 2
#
#     track=Track([track[0]])
#     track.MCtruthClassifyTrack(label)
#
#
#
#     track.DecorateSegments(segments)
#     GoodTracks.append(track)
#     del track
#     continue
#
# print('The raw image generation has been completed..')
# del tracks
# del segments
# gc.collect()
# print(UF.TimeStamp(),'Saving the results..')
#
#
#
# UF.LogOperations(output_file_location,'w',GoodTracks) #Writing the remaining data into the csv
# print(UF.TimeStamp(), "Train seed generation is finished...")
#End of the script



