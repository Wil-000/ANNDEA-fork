###This file contains the utility functions that are commonly used in EDER_VIANN packages

import csv
import math
import os
import subprocess
import datetime
import numpy as np
import copy
from statistics import mean
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
#from scipy.stats import chisquare

#This utility provides Timestamps for print messages
def TimeStamp():
 return "["+datetime.datetime.now().strftime("%D")+' '+datetime.datetime.now().strftime("%H:%M:%S")+"]"

class TrainingSampleMeta:
      def __init__(self,TrainDataID):
          self.TrainDataID=TrainDataID
      def __eq__(self, other):
        return (self.TrainDataID) == (other.TrainDataID)
      def __hash__(self):
        return hash(self.TrainDataID)
      def IniHitClusterMetaData(self,stepX,stepY,stepZ,cut_dt,cut_dr,testRatio,valRatio,z_offset,y_offset,x_offset, Xsteps, Zsteps,X_overlap,Y_overlap,Z_overlap):
          self.stepX=stepX
          self.stepY=stepY
          self.stepZ=stepZ
          self.cut_dt=cut_dt
          self.cut_dr=cut_dr
          self.testRatio=testRatio
          self.valRatio=valRatio
          self.z_offset=z_offset
          self.y_offset=y_offset
          self.x_offset=x_offset
          self.Xsteps=Xsteps
          self.Zsteps=Zsteps
          self.X_overlap=X_overlap
          self.Y_overlap=Y_overlap
          self.Z_overlap=Z_overlap
      def IniTrackSeedMetaData(self,MaxSLG,MaxSTG,MaxDOCA,MaxAngle,JobSets,MaxSegments,VetoMotherTrack):
          self.MaxSLG=MaxSLG
          self.MaxSTG=MaxSTG
          self.MaxDOCA=MaxDOCA
          self.MaxAngle=MaxAngle
          self.JobSets=JobSets
          self.MaxSegments=MaxSegments
          self.VetoMotherTrack=VetoMotherTrack

      def UpdateHitClusterMetaData(self,NoS,NoNF,NoEF,NoSets):
          self.num_node_features=NoNF
          self.num_edge_features=NoEF
          self.tot_sample_size=NoS
          self.no_sets=NoSets
def GetEquationOfLine(Data):
          x=[]
          for i in range(0,len(Data)):
              x.append(i)
          line=np.polyfit(x,Data,1)
          return line
class ModelMeta:
      def __init__(self,ModelID):
          self.ModelID=ModelID
      def __eq__(self, other):
        return (self.ModelID) == (other.ModelID)
      def __hash__(self):
        return hash(self.ModelID)
      def IniModelMeta(self, ModelParams, framework, DataMeta, architecture, type):
          self.ModelParameters=ModelParams
          self.ModelFramework=framework
          self.ModelArchitecture=architecture
          self.ModelType=type
          self.TrainSessionsDataID=[]
          self.TrainSessionsDateTime=[]
          self.TrainSessionsParameters=[]
          self.TrainSessionsData=[]
          if (self.ModelFramework=='PyTorch') and (self.ModelArchitecture=='TCN'):
              self.num_node_features=DataMeta.num_node_features
              self.num_edge_features=DataMeta.num_edge_features
              self.stepX=DataMeta.stepX
              self.stepY=DataMeta.stepY
              self.stepZ=DataMeta.stepZ
              self.cut_dt=DataMeta.cut_dt
              self.cut_dr=DataMeta.cut_dr
      def IniTrainingSession(self, TrainDataID, DateTime, TrainParameters):
          self.TrainSessionsDataID.append(TrainDataID)
          self.TrainSessionsDateTime.append(DateTime)
          self.TrainSessionsParameters.append(TrainParameters)
      def CompleteTrainingSession(self, TrainData):
          self.TrainSessionsData.append(TrainData)


class HitCluster:
      def __init__(self,ClusterID, Step):
          self.ClusterID=ClusterID
          self.Step=Step
      def __eq__(self, other):
        return ('-'.join(str(self.ClusterID))) == ('-'.join(str(other.ClusterID)))
      def __hash__(self):
        return hash(('-'.join(str(self.ClusterID))))
      def LoadClusterHits(self,RawHits): #Decorate hit information
           self.ClusterHits=[]
           self.ClusterHitIDs=[]
           __ClusterHitsTemp=[]
           for s in RawHits:
               if s[1]>=self.ClusterID[0]*self.Step[0] and s[1]<((self.ClusterID[0]+1)*self.Step[0]):
                   if s[2]>=self.ClusterID[1]*self.Step[1] and s[2]<((self.ClusterID[1]+1)*self.Step[1]):
                       if s[3]>=self.ClusterID[2]*self.Step[2] and s[3]<((self.ClusterID[2]+1)*self.Step[2]):
                          __ClusterHitsTemp.append([(s[1]-(self.ClusterID[0]*self.Step[0]))/self.Step[2],(s[2]-(self.ClusterID[1]*self.Step[1]))/self.Step[2], (s[3]-(self.ClusterID[2]*self.Step[2]))/self.Step[2],((s[4])+1)/2, ((s[5])+1)/2])
                          self.ClusterHitIDs.append(s[0])
                          self.ClusterHits.append(s)
           self.ClusterSize=len(__ClusterHitsTemp)
           import torch
           import torch_geometric
           from torch_geometric.data import Data
           self.ClusterGraph=Data(x=torch.Tensor(__ClusterHitsTemp), edge_index=None, y=None)
           del __ClusterHitsTemp
      def GenerateTrainData(self, MCHits,cut_dt, cut_dr): #Decorate hit information
           import pandas as pd
           _MCClusterHits=[]
           for s in MCHits:
               if s[1]>=self.ClusterID[0]*self.Step[0] and s[1]<((self.ClusterID[0]+1)*self.Step[0]):
                   if s[2]>=self.ClusterID[1]*self.Step[1] and s[2]<((self.ClusterID[1]+1)*self.Step[1]):
                       if s[3]>=self.ClusterID[2]*self.Step[2] and s[3]<((self.ClusterID[2]+1)*self.Step[2]):
                          _MCClusterHits.append([s[0],s[6]])
           #Preparing Raw and MC combined data 1
           _l_MCHits=pd.DataFrame(_MCClusterHits, columns = ['l_HitID','l_MC_ID'])
           _l_Hits=pd.DataFrame(self.ClusterHits, columns = ['l_HitID','l_x','l_y','l_z','l_tx','l_ty'])
           #Join hits + MC truth
           _l_Tot_Hits=pd.merge(_l_MCHits, _l_Hits, how="right", on=['l_HitID'])
           _l_Tot_Hits['join_key'] = 'join_key'

           #Preparing Raw and MC combined data 2
           _r_MCHits=pd.DataFrame(_MCClusterHits, columns = ['r_HitID','r_MC_ID'])
           _r_Hits=pd.DataFrame(self.ClusterHits, columns = ['r_HitID','r_x','r_y','r_z','r_tx','r_ty'])
           #Join hits + MC truth
           _r_Tot_Hits=pd.merge(_r_MCHits, _r_Hits, how="right", on=['r_HitID'])
           _r_Tot_Hits['join_key'] = 'join_key'

           #Combining data 1 and 2
           _Tot_Hits=pd.merge(_l_Tot_Hits, _r_Tot_Hits, how="inner", on=['join_key'])
           _Tot_Hits.l_MC_ID= _Tot_Hits.l_MC_ID.fillna(_Tot_Hits.l_HitID)
           _Tot_Hits.r_MC_ID= _Tot_Hits.r_MC_ID.fillna(_Tot_Hits.r_HitID)
           _Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['l_HitID'] == _Tot_Hits['r_HitID']], inplace = True)
           _Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['l_z'] <= _Tot_Hits['r_z']], inplace = True)
           _Tot_Hits['d_tx'] = _Tot_Hits['l_tx']-_Tot_Hits['r_tx']
           _Tot_Hits['d_tx'] = _Tot_Hits['d_tx'].abs()
           _Tot_Hits['d_ty'] = _Tot_Hits['l_ty']-_Tot_Hits['r_ty']
           _Tot_Hits['d_ty'] = _Tot_Hits['d_ty'].abs()
           _Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['d_tx'] >= cut_dt], inplace = True)
           _Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['d_ty'] >= cut_dt], inplace = True)
           _Tot_Hits['d_x'] = (_Tot_Hits['r_x']-(_Tot_Hits['l_x']+(_Tot_Hits['l_tx']*(_Tot_Hits['r_z']-_Tot_Hits['l_z']))))
           _Tot_Hits['d_x'] = _Tot_Hits['d_x'].abs()
           _Tot_Hits['d_y'] = (_Tot_Hits['r_y']-(_Tot_Hits['l_y']+(_Tot_Hits['l_ty']*(_Tot_Hits['r_z']-_Tot_Hits['l_z']))))
           _Tot_Hits['d_y'] = _Tot_Hits['d_y'].abs()
           _Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['d_x'] >= cut_dr], inplace = True)
           _Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['d_y'] >= cut_dr], inplace = True)

           #_Tot_Hits = _Tot_Hits.drop(['d_tx','d_ty','d_x','d_y','join_key','l_tx','l_ty','r_tx','r_ty'],axis=1)
           _Tot_Hits = _Tot_Hits.drop(['d_x','d_y','join_key','l_tx','l_ty','r_tx','r_ty'],axis=1)
           _Tot_Hits['l_x']=_Tot_Hits['l_x']/self.Step[2]
           _Tot_Hits['l_y']=_Tot_Hits['l_y']/self.Step[2]
           _Tot_Hits['l_z']=_Tot_Hits['l_z']/self.Step[2]
           _Tot_Hits['r_x']=_Tot_Hits['r_x']/self.Step[2]
           _Tot_Hits['r_y']=_Tot_Hits['r_y']/self.Step[2]
           _Tot_Hits['r_z']=_Tot_Hits['r_z']/self.Step[2]
           _Tot_Hits['label']=(_Tot_Hits['l_MC_ID']==_Tot_Hits['r_MC_ID']).astype('int8')
           _Tot_Hits['d_l'] = (np.sqrt(((_Tot_Hits['r_y']-_Tot_Hits['l_y'])**2) + ((_Tot_Hits['r_x']-_Tot_Hits['l_x'])**2) + ((_Tot_Hits['r_z']-_Tot_Hits['l_z'])**2)))
           _Tot_Hits['d_t'] = np.sqrt(((_Tot_Hits['r_y']-_Tot_Hits['l_y'])**2) + ((_Tot_Hits['r_x']-_Tot_Hits['l_x'])**2))
           _Tot_Hits['d_z'] = (_Tot_Hits['r_z']-_Tot_Hits['l_z']).abs()

           _Tot_Hits = _Tot_Hits.drop(['r_x','r_y','r_z','l_x','l_y','l_z','l_MC_ID','r_MC_ID'],axis=1)
           _Tot_Hits=_Tot_Hits[['l_HitID','r_HitID','label','d_l','d_t','d_z','d_tx','d_ty']]
           _Tot_Hits=_Tot_Hits.values.tolist()
           import torch
           self.ClusterGraph.edge_index=torch.tensor((HitCluster.GenerateLinks(_Tot_Hits,self.ClusterHitIDs)))
           self.ClusterGraph.edge_attr=torch.tensor((HitCluster.GenerateEdgeAttributes(_Tot_Hits)))
           self.ClusterGraph.y=torch.tensor((HitCluster.GenerateEdgeLabels(_Tot_Hits)))
           if len(self.ClusterGraph.x)>0:
               return True
           else:
               return False
      def GenerateEdges(self, cut_dt, cut_dr): #Decorate hit information
           import pandas as pd
           #Preparing Raw and MC combined data 1
           _l_Hits=pd.DataFrame(self.ClusterHits, columns = ['l_HitID','l_x','l_y','l_z','l_tx','l_ty'])
           #Join hits + MC truth
           _l_Hits['join_key'] = 'join_key'
           #Preparing Raw and MC combined data 2
           _r_Hits=pd.DataFrame(self.ClusterHits, columns = ['r_HitID','r_x','r_y','r_z','r_tx','r_ty'])
           #Join hits + MC truth
           _r_Hits['join_key'] = 'join_key'

           #Combining data 1 and 2
           _Tot_Hits=pd.merge(_l_Hits, _r_Hits, how="inner", on=['join_key'])
           _Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['l_HitID'] == _Tot_Hits['r_HitID']], inplace = True)
           _Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['l_z'] <= _Tot_Hits['r_z']], inplace = True)
           _Tot_Hits['d_tx'] = _Tot_Hits['l_tx']-_Tot_Hits['r_tx']
           _Tot_Hits['d_tx'] = _Tot_Hits['d_tx'].abs()
           _Tot_Hits['d_ty'] = _Tot_Hits['l_ty']-_Tot_Hits['r_ty']
           _Tot_Hits['d_ty'] = _Tot_Hits['d_ty'].abs()
           _Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['d_tx'] >= cut_dt], inplace = True)
           _Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['d_ty'] >= cut_dt], inplace = True)
           _Tot_Hits['d_x'] = (_Tot_Hits['r_x']-(_Tot_Hits['l_x']+(_Tot_Hits['l_tx']*(_Tot_Hits['r_z']-_Tot_Hits['l_z']))))
           _Tot_Hits['d_x'] = _Tot_Hits['d_x'].abs()
           _Tot_Hits['d_y'] = (_Tot_Hits['r_y']-(_Tot_Hits['l_y']+(_Tot_Hits['l_ty']*(_Tot_Hits['r_z']-_Tot_Hits['l_z']))))
           _Tot_Hits['d_y'] = _Tot_Hits['d_y'].abs()
           _Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['d_x'] >= cut_dr], inplace = True)
           _Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['d_y'] >= cut_dr], inplace = True)

           #_Tot_Hits = _Tot_Hits.drop(['d_tx','d_ty','d_x','d_y','join_key','l_tx','l_ty','r_tx','r_ty'],axis=1)
           _Tot_Hits = _Tot_Hits.drop(['d_x','d_y','join_key','l_tx','l_ty','r_tx','r_ty'],axis=1)
           _Tot_Hits['l_x']=_Tot_Hits['l_x']/self.Step[2]
           _Tot_Hits['l_y']=_Tot_Hits['l_y']/self.Step[2]
           _Tot_Hits['l_z']=_Tot_Hits['l_z']/self.Step[2]
           _Tot_Hits['r_x']=_Tot_Hits['r_x']/self.Step[2]
           _Tot_Hits['r_y']=_Tot_Hits['r_y']/self.Step[2]
           _Tot_Hits['r_z']=_Tot_Hits['r_z']/self.Step[2]
           _Tot_Hits['label']='N/A'
           _Tot_Hits['d_l'] = (np.sqrt(((_Tot_Hits['r_y']-_Tot_Hits['l_y'])**2) + ((_Tot_Hits['r_x']-_Tot_Hits['l_x'])**2) + ((_Tot_Hits['r_z']-_Tot_Hits['l_z'])**2)))
           _Tot_Hits['d_t'] = np.sqrt(((_Tot_Hits['r_y']-_Tot_Hits['l_y'])**2) + ((_Tot_Hits['r_x']-_Tot_Hits['l_x'])**2))
           _Tot_Hits['d_z'] = (_Tot_Hits['r_z']-_Tot_Hits['l_z']).abs()
           _Tot_Hits = _Tot_Hits.drop(['r_x','r_y','r_z','l_x','l_y','l_z'],axis=1)
           _Tot_Hits=_Tot_Hits[['l_HitID','r_HitID','label','d_l','d_t','d_z','d_tx','d_ty']]
           _Tot_Hits=_Tot_Hits.values.tolist()
           import torch
           self.ClusterGraph.edge_index=torch.tensor((HitCluster.GenerateLinks(_Tot_Hits,self.ClusterHitIDs)))
           self.ClusterGraph.edge_attr=torch.tensor((HitCluster.GenerateEdgeAttributes(_Tot_Hits)))
           self.edges=[]
           for r in _Tot_Hits:
               self.edges.append(r[:2])
           if len(self.ClusterGraph.edge_attr)>0:
               return True
           else:
               return False

      def LinkHits(self,hits,GiveStats,MCHits,cut_dt,cut_dr, Acceptance):
          self.HitLinks=hits
          import pandas as pd
          _Hits_df=pd.DataFrame(self.ClusterHits, columns = ['_l_HitID','x','y','z','tx','ty'])
          _Hits_df["x"] = pd.to_numeric(_Hits_df["x"],downcast='float')
          _Hits_df["y"] = pd.to_numeric(_Hits_df["y"],downcast='float')
          _Hits_df["z"] = pd.to_numeric(_Hits_df["z"],downcast='float')
          _Hits_df["tx"] = pd.to_numeric(_Hits_df["tx"],downcast='float')
          _Hits_df["ty"] = pd.to_numeric(_Hits_df["ty"],downcast='float')
          if GiveStats:
            _Hits_df['dummy_join']='dummy_join'
            _MCClusterHits=[]
            StatFakeValues=[]
            StatTruthValues=[]
            StatLabels=['Initial # of combinations','Delete self-permutations','Enforce positive directionality','Cut on delta t', 'Cut on delta x','Acceptance Cut','Segment Reconstruction']
            for s in MCHits:
               if s[1]>=self.ClusterID[0]*self.Step[0] and s[1]<((self.ClusterID[0]+1)*self.Step[0]):
                   if s[2]>=self.ClusterID[1]*self.Step[1] and s[2]<((self.ClusterID[1]+1)*self.Step[1]):
                       if s[3]>=self.ClusterID[2]*self.Step[2] and s[3]<((self.ClusterID[2]+1)*self.Step[2]):
                          _MCClusterHits.append([s[0],s[6]])
           #Preparing Raw and MC combined data 1
            _l_MCHits=pd.DataFrame(_MCClusterHits, columns = ['_l_HitID','l_MC_ID'])
            _r_MCHits=pd.DataFrame(_MCClusterHits, columns = ['_r_HitID','l_MC_ID'])
            _l_Hits=_Hits_df.rename(columns={"x": "l_x", "y": "l_y", "z": "l_z", "tx": "l_tx","ty": "l_ty"})
            #Join hits + MC truth
            _l_Tot_Hits=pd.merge(_l_MCHits, _l_Hits, how="right", on=['_l_HitID'])
            #Preparing Raw and MC combined data 2
            _r_MCHits=pd.DataFrame(_MCClusterHits, columns = ['_r_HitID','r_MC_ID'])
            _r_Hits=_Hits_df[['_l_HitID', 'x', 'y', 'z', 'tx', 'ty', 'dummy_join']].rename(columns={"x": "r_x", "y": "r_y", "z": "r_z", "tx": "r_tx","ty": "r_ty","_l_HitID": "_r_HitID" })
            #Join hits + MC truth
            _r_Tot_Hits=pd.merge(_r_MCHits, _r_Hits, how="right", on=['_r_HitID'])
            _r_Tot_Hits.drop_duplicates(subset=['_r_HitID'],keep='first', inplace=True)
            _Tot_Hits=pd.merge(_l_Tot_Hits, _r_Tot_Hits, how="inner", on=["dummy_join"])
            _Tot_Hits.l_MC_ID= _Tot_Hits.l_MC_ID.fillna(_Tot_Hits._l_HitID)
            _Tot_Hits.r_MC_ID= _Tot_Hits.r_MC_ID.fillna(_Tot_Hits._r_HitID)
            _Tot_Hits.drop_duplicates(subset=['_l_HitID','_r_HitID'],keep='first', inplace=True)
            StatFakeValues.append(len(_Tot_Hits.axes[0])-len(_Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['l_MC_ID'] != _Tot_Hits['r_MC_ID']]).axes[0]))
            StatTruthValues.append(len(_Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['l_MC_ID'] != _Tot_Hits['r_MC_ID']]).axes[0]))
            _Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['_l_HitID'] == _Tot_Hits['_r_HitID']], inplace = True)
            StatFakeValues.append(len(_Tot_Hits.axes[0])-len(_Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['l_MC_ID'] != _Tot_Hits['r_MC_ID']]).axes[0]))
            StatTruthValues.append(len(_Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['l_MC_ID'] != _Tot_Hits['r_MC_ID']]).axes[0]))
            _Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['l_z'] <= _Tot_Hits['r_z']], inplace = True)
            StatFakeValues.append(len(_Tot_Hits.axes[0])-len(_Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['l_MC_ID'] != _Tot_Hits['r_MC_ID']]).axes[0]))
            StatTruthValues.append(len(_Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['l_MC_ID'] != _Tot_Hits['r_MC_ID']]).axes[0]))
            _Tot_Hits['d_tx'] = _Tot_Hits['l_tx']-_Tot_Hits['r_tx']
            _Tot_Hits['d_tx'] = _Tot_Hits['d_tx'].abs()
            _Tot_Hits['d_ty'] = _Tot_Hits['l_ty']-_Tot_Hits['r_ty']
            _Tot_Hits['d_ty'] = _Tot_Hits['d_ty'].abs()
            _Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['d_tx'] >= cut_dt], inplace = True)
            _Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['d_ty'] >= cut_dt], inplace = True)
            StatFakeValues.append(len(_Tot_Hits.axes[0])-len(_Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['l_MC_ID'] != _Tot_Hits['r_MC_ID']]).axes[0]))
            StatTruthValues.append(len(_Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['l_MC_ID'] != _Tot_Hits['r_MC_ID']]).axes[0]))
            _Tot_Hits['d_x'] = (_Tot_Hits['r_x']-(_Tot_Hits['l_x']+(_Tot_Hits['l_tx']*(_Tot_Hits['r_z']-_Tot_Hits['l_z']))))
            _Tot_Hits['d_x'] = _Tot_Hits['d_x'].abs()
            _Tot_Hits['d_y'] = (_Tot_Hits['r_y']-(_Tot_Hits['l_y']+(_Tot_Hits['l_ty']*(_Tot_Hits['r_z']-_Tot_Hits['l_z']))))
            _Tot_Hits['d_y'] = _Tot_Hits['d_y'].abs()
            _Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['d_x'] >= cut_dr], inplace = True)
            _Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['d_y'] >= cut_dr], inplace = True)
            StatFakeValues.append(len(_Tot_Hits.axes[0])-len(_Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['l_MC_ID'] != _Tot_Hits['r_MC_ID']]).axes[0]))
            StatTruthValues.append(len(_Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['l_MC_ID'] != _Tot_Hits['r_MC_ID']]).axes[0]))
            _Map_df=pd.DataFrame(self.HitLinks, columns = ['_l_HitID','_r_HitID','link_strength'])
            _Tot_Hits=pd.merge(_Tot_Hits, _Map_df, how="inner", on=['_l_HitID','_r_HitID'])
            _Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['link_strength'] <= Acceptance], inplace = True)
            StatFakeValues.append(len(_Tot_Hits.axes[0])-len(_Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['l_MC_ID'] != _Tot_Hits['r_MC_ID']]).axes[0]))
            StatTruthValues.append(len(_Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['l_MC_ID'] != _Tot_Hits['r_MC_ID']]).axes[0]))
            _Tot_Hits=_Tot_Hits[['_r_HitID','_l_HitID','r_z','l_z','link_strength']]
            _Tot_Hits.sort_values(by = ['_r_HitID', 'l_z','link_strength'], ascending=[True,True, False],inplace=True)
            _Loc_Hits_r=_Tot_Hits[['r_z']].rename(columns={'r_z': 'z'})
            _Loc_Hits_l=_Tot_Hits[['l_z']].rename(columns={'l_z': 'z'})
            _Loc_Hits=pd.concat([_Loc_Hits_r,_Loc_Hits_l])
            _Loc_Hits.sort_values(by = ['z'], ascending=[True],inplace=True)
            _Loc_Hits.drop_duplicates(subset=['z'], keep='first', inplace=True)
            _Loc_Hits=_Loc_Hits.reset_index(drop=True)
            _Loc_Hits=_Loc_Hits.reset_index()
            _Loc_Hits_r=_Loc_Hits.rename(columns={'index': 'r_index', 'z': 'r_z'})
            _Loc_Hits_l=_Loc_Hits.rename(columns={'index': 'l_index', 'z': 'l_z'})
            _Tot_Hits=pd.merge(_Tot_Hits,_Loc_Hits_r, how='inner', on=['r_z'])
            _Tot_Hits=pd.merge(_Tot_Hits,_Loc_Hits_l, how='inner', on=['l_z'])
            _Tot_Hits=_Tot_Hits[['_r_HitID','_l_HitID','r_index','l_index','link_strength']]

            _Tot_Hits.sort_values(by = ['_r_HitID', 'l_index','link_strength'], ascending=[True,True, False],inplace=True)
            _Tot_Hits.drop_duplicates(subset=['_r_HitID', 'l_index','link_strength'], keep='first', inplace=True)

            _Tot_Hits.sort_values(by = ['_l_HitID', 'r_index','link_strength'], ascending=[True,True, False],inplace=True)
            _Tot_Hits.drop_duplicates(subset=['_l_HitID', 'r_index','link_strength'], keep='first', inplace=True)

            _Tot_Hits=_Tot_Hits.values.tolist()

            _Temp_Tot_Hits=[]
            for el in _Tot_Hits:
                _Temp_Tot_Hit_El = [[],[]]
                for pos in range(len(_Loc_Hits)):
                    if pos==el[2]:
                        _Temp_Tot_Hit_El[0].append(el[0])
                        _Temp_Tot_Hit_El[1].append(el[4])
                    elif pos==el[3]:
                        _Temp_Tot_Hit_El[0].append(el[1])
                        _Temp_Tot_Hit_El[1].append(el[4])
                    else:
                        _Temp_Tot_Hit_El[0].append('_')
                        _Temp_Tot_Hit_El[1].append(0.0)
                _Temp_Tot_Hits.append(_Temp_Tot_Hit_El)
            _Tot_Hits=_Temp_Tot_Hits
            _Rec_Hits_Pool=[]
            _intital_size=len(_Tot_Hits)

            while len(_Tot_Hits)>0:
                _Tot_Hits_PCopy=copy.deepcopy(_Tot_Hits)
                _Tot_Hits_Predator=[]
                for Predator in _Tot_Hits_PCopy:
                    for Prey in _Tot_Hits_PCopy:
                          if Predator!=Prey:
                           Predator=HitCluster.InjectHit(Predator,Prey,False)[0]
                    _Tot_Hits_Predator.append(Predator)
                for s in _Tot_Hits_Predator:
                    s=s[0].append(mean(s.pop(1)))
                _Tot_Hits_Predator = [item for l in _Tot_Hits_Predator for item in l]
                #_Tot_Hits_Predator_Mirror=[]
                for s in range(len(_Tot_Hits_Predator)):
                    for h in range(len(_Tot_Hits_Predator[s])):
                        if _Tot_Hits_Predator[s][h] =='_':
                            _Tot_Hits_Predator[s][h]='H_'+str(s)

                column_no=len(_Tot_Hits_Predator[0])-1
                columns=[]

                for c in range(column_no):
                    columns.append(str(c))
                columns.append('average_link_strength')
                _Tot_Hits_Predator=pd.DataFrame(_Tot_Hits_Predator, columns = columns)
                _Tot_Hits_Predator.sort_values(by = ['average_link_strength'], ascending=[False],inplace=True)
                for c in range(column_no):
                    _Tot_Hits_Predator.drop_duplicates(subset=[str(c)], keep='first', inplace=True)
                _Tot_Hits_Predator=_Tot_Hits_Predator.drop(['average_link_strength'],axis=1)

                _Tot_Hits_Predator=_Tot_Hits_Predator.values.tolist()
                for seg in range(len(_Tot_Hits_Predator)):
                    _Tot_Hits_Predator[seg]=[s for s in _Tot_Hits_Predator[seg] if ('H' in s)==False]
                _Rec_Hits_Pool+=_Tot_Hits_Predator
                for seg in _Tot_Hits_Predator:
                    _itr=0
                    while _itr<len(_Tot_Hits):
                        if HitCluster.InjectHit(seg,_Tot_Hits[_itr],True):
                            del _Tot_Hits[_itr]
                        else:
                            _itr+=1
            #Transpose the rows
            _track_list=[]
            _segment_id=str(self.ClusterID[0])
            for el in self.ClusterID:
                _segment_id+=('-'+str(el))
            for t in range(len(_Rec_Hits_Pool)):
                for h in _Rec_Hits_Pool[t]:
                    _track_list.append([_segment_id+'-'+str(t+1),h])
            _Rec_Hits_Pool=pd.DataFrame(_track_list, columns = ['Segment_ID','HitID'])
            _Hits_df=pd.DataFrame(self.ClusterHits, columns = ['HitID','x','y','z','tx','ty'])
            _Hits_df=_Hits_df[['HitID','z']]
            #Join hits + MC truth
            _Rec_Hits_Pool=pd.merge(_Hits_df, _Rec_Hits_Pool, how="right", on=['HitID'])
            self.RecHits=_Rec_Hits_Pool

            _Rec_Hits_Pool_l=pd.DataFrame(_track_list, columns = ['Segment_ID','_l_HitID'])
            _Rec_Hits_Pool_r=pd.DataFrame(_track_list, columns = ['Segment_ID','_r_HitID'])
            #Join hits + MC truth
            _Rec_Hits_Pool_r=pd.merge(_r_MCHits, _Rec_Hits_Pool_r, how="right", on=['_r_HitID'])
            _Rec_Hits_Pool_l=pd.merge(_l_MCHits, _Rec_Hits_Pool_l, how="right", on=['_l_HitID'])
            _Rec_Hits_Pool=pd.merge(_Rec_Hits_Pool_l, _Rec_Hits_Pool_r, how="inner",on=["Segment_ID"])
            _Rec_Hits_Pool.l_MC_ID= _Rec_Hits_Pool.l_MC_ID.fillna(_Rec_Hits_Pool._l_HitID)
            _Rec_Hits_Pool.r_MC_ID= _Rec_Hits_Pool.r_MC_ID.fillna(_Rec_Hits_Pool._r_HitID)
            _Rec_Hits_Pool.drop(_Rec_Hits_Pool.index[_Rec_Hits_Pool['_l_HitID'] == _Rec_Hits_Pool['_r_HitID']], inplace = True)
            _Rec_Hits_Pool["Pair_ID"]= ['-'.join(sorted(tup)) for tup in zip(_Rec_Hits_Pool['_l_HitID'], _Rec_Hits_Pool['_r_HitID'])]
            _Rec_Hits_Pool.drop_duplicates(subset="Pair_ID",keep='first',inplace=True)
            StatFakeValues.append(len(_Rec_Hits_Pool.axes[0])-len(_Rec_Hits_Pool.drop(_Rec_Hits_Pool.index[_Rec_Hits_Pool['l_MC_ID'] != _Rec_Hits_Pool['r_MC_ID']]).axes[0]))
            StatTruthValues.append(len(_Rec_Hits_Pool.drop(_Rec_Hits_Pool.index[_Rec_Hits_Pool['l_MC_ID'] != _Rec_Hits_Pool['r_MC_ID']]).axes[0]))
            self.RecStats=[StatLabels,StatFakeValues,StatTruthValues]
          else:
            _Hits_df['dummy_join']='dummy_join'
            _l_Hits=_Hits_df.rename(columns={"x": "l_x", "y": "l_y", "z": "l_z", "tx": "l_tx","ty": "l_ty"})
            _r_Hits=_Hits_df[['_l_HitID', 'x', 'y', 'z', 'tx', 'ty', 'dummy_join']].rename(columns={"x": "r_x", "y": "r_y", "z": "r_z", "tx": "r_tx","ty": "r_ty","_l_HitID": "_r_HitID" })
            _Tot_Hits=pd.merge(_l_Hits, _r_Hits, how="inner", on=["dummy_join"])
            _Tot_Hits.drop_duplicates(subset=['_l_HitID','_r_HitID'],keep='first', inplace=True)
            _Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['_l_HitID'] == _Tot_Hits['_r_HitID']], inplace = True)
            _Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['l_z'] <= _Tot_Hits['r_z']], inplace = True)
            _Tot_Hits['d_tx'] = _Tot_Hits['l_tx']-_Tot_Hits['r_tx']
            _Tot_Hits['d_tx'] = _Tot_Hits['d_tx'].abs()
            _Tot_Hits['d_ty'] = _Tot_Hits['l_ty']-_Tot_Hits['r_ty']
            _Tot_Hits['d_ty'] = _Tot_Hits['d_ty'].abs()
            _Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['d_tx'] >= cut_dt], inplace = True)
            _Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['d_ty'] >= cut_dt], inplace = True)
            _Tot_Hits['d_x'] = (_Tot_Hits['r_x']-(_Tot_Hits['l_x']+(_Tot_Hits['l_tx']*(_Tot_Hits['r_z']-_Tot_Hits['l_z']))))
            _Tot_Hits['d_x'] = _Tot_Hits['d_x'].abs()
            _Tot_Hits['d_y'] = (_Tot_Hits['r_y']-(_Tot_Hits['l_y']+(_Tot_Hits['l_ty']*(_Tot_Hits['r_z']-_Tot_Hits['l_z']))))
            _Tot_Hits['d_y'] = _Tot_Hits['d_y'].abs()
            _Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['d_x'] >= cut_dr], inplace = True)
            _Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['d_y'] >= cut_dr], inplace = True)
            _Map_df=pd.DataFrame(self.HitLinks, columns = ['_l_HitID','_r_HitID','link_strength'])
            _Tot_Hits=pd.merge(_Tot_Hits, _Map_df, how="inner", on=['_l_HitID','_r_HitID'])
            _Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['link_strength'] <= Acceptance], inplace = True)
            _Tot_Hits=_Tot_Hits[['_r_HitID','_l_HitID','r_z','l_z','link_strength']]
            _Tot_Hits.sort_values(by = ['_r_HitID', 'l_z','link_strength'], ascending=[True,True, False],inplace=True)
            _Loc_Hits_r=_Tot_Hits[['r_z']].rename(columns={'r_z': 'z'})
            _Loc_Hits_l=_Tot_Hits[['l_z']].rename(columns={'l_z': 'z'})
            _Loc_Hits=pd.concat([_Loc_Hits_r,_Loc_Hits_l])
            _Loc_Hits.sort_values(by = ['z'], ascending=[True],inplace=True)
            _Loc_Hits.drop_duplicates(subset=['z'], keep='first', inplace=True)
            _Loc_Hits=_Loc_Hits.reset_index(drop=True)
            _Loc_Hits=_Loc_Hits.reset_index()
            _Loc_Hits_r=_Loc_Hits.rename(columns={'index': 'r_index', 'z': 'r_z'})
            _Loc_Hits_l=_Loc_Hits.rename(columns={'index': 'l_index', 'z': 'l_z'})
            _Tot_Hits=pd.merge(_Tot_Hits,_Loc_Hits_r, how='inner', on=['r_z'])
            _Tot_Hits=pd.merge(_Tot_Hits,_Loc_Hits_l, how='inner', on=['l_z'])
            _Tot_Hits=_Tot_Hits[['_r_HitID','_l_HitID','r_index','l_index','link_strength']]
            _Tot_Hits.sort_values(by = ['_r_HitID', 'l_index','link_strength'], ascending=[True,True, False],inplace=True)
            _Tot_Hits.drop_duplicates(subset=['_r_HitID', 'l_index','link_strength'], keep='first', inplace=True)
            _Tot_Hits.sort_values(by = ['_l_HitID', 'r_index','link_strength'], ascending=[True,True, False],inplace=True)
            _Tot_Hits.drop_duplicates(subset=['_l_HitID', 'r_index','link_strength'], keep='first', inplace=True)
            _Tot_Hits=_Tot_Hits.values.tolist()
            _Temp_Tot_Hits=[]
            for el in _Tot_Hits:
                _Temp_Tot_Hit_El = [[],[]]
                for pos in range(len(_Loc_Hits)):
                    if pos==el[2]:
                        _Temp_Tot_Hit_El[0].append(el[0])
                        _Temp_Tot_Hit_El[1].append(el[4])
                    elif pos==el[3]:
                        _Temp_Tot_Hit_El[0].append(el[1])
                        _Temp_Tot_Hit_El[1].append(el[4])
                    else:
                        _Temp_Tot_Hit_El[0].append('_')
                        _Temp_Tot_Hit_El[1].append(0.0)
                _Temp_Tot_Hits.append(_Temp_Tot_Hit_El)
            _Tot_Hits=_Temp_Tot_Hits
            _Rec_Hits_Pool=[]
            _intital_size=len(_Tot_Hits)

            while len(_Tot_Hits)>0:
                _Tot_Hits_PCopy=copy.deepcopy(_Tot_Hits)
                _Tot_Hits_Predator=[]
                for Predator in _Tot_Hits_PCopy:
                    for Prey in _Tot_Hits_PCopy:
                          if Predator!=Prey:
                           Predator=HitCluster.InjectHit(Predator,Prey,False)[0]
                    _Tot_Hits_Predator.append(Predator)
                for s in _Tot_Hits_Predator:
                    s=s[0].append(mean(s.pop(1)))
                _Tot_Hits_Predator = [item for l in _Tot_Hits_Predator for item in l]
                #_Tot_Hits_Predator_Mirror=[]
                for s in range(len(_Tot_Hits_Predator)):
                    for h in range(len(_Tot_Hits_Predator[s])):
                        if _Tot_Hits_Predator[s][h] =='_':
                            _Tot_Hits_Predator[s][h]='H_'+str(s)

                column_no=len(_Tot_Hits_Predator[0])-1
                columns=[]

                for c in range(column_no):
                    columns.append(str(c))
                columns.append('average_link_strength')
                _Tot_Hits_Predator=pd.DataFrame(_Tot_Hits_Predator, columns = columns)
                _Tot_Hits_Predator.sort_values(by = ['average_link_strength'], ascending=[False],inplace=True)
                for c in range(column_no):
                    _Tot_Hits_Predator.drop_duplicates(subset=[str(c)], keep='first', inplace=True)
                _Tot_Hits_Predator=_Tot_Hits_Predator.drop(['average_link_strength'],axis=1)

                _Tot_Hits_Predator=_Tot_Hits_Predator.values.tolist()
                for seg in range(len(_Tot_Hits_Predator)):
                    _Tot_Hits_Predator[seg]=[s for s in _Tot_Hits_Predator[seg] if ('H' in s)==False]
                _Rec_Hits_Pool+=_Tot_Hits_Predator
                for seg in _Tot_Hits_Predator:
                    _itr=0
                    while _itr<len(_Tot_Hits):
                        if HitCluster.InjectHit(seg,_Tot_Hits[_itr],True):
                            del _Tot_Hits[_itr]
                        else:
                            _itr+=1
            #Transpose the rows
            _track_list=[]
            _segment_id=str(self.ClusterID[0])
            for el in self.ClusterID:
                _segment_id+=('-'+str(el))
            for t in range(len(_Rec_Hits_Pool)):
                for h in _Rec_Hits_Pool[t]:
                    _track_list.append([_segment_id+'-'+str(t+1),h])
            _Rec_Hits_Pool=pd.DataFrame(_track_list, columns = ['Segment_ID','HitID'])
            _Hits_df=pd.DataFrame(self.ClusterHits, columns = ['HitID','x','y','z','tx','ty'])
            _Hits_df=_Hits_df[['HitID','z']]
            #Join hits + MC truth
            _Rec_Hits_Pool=pd.merge(_Hits_df, _Rec_Hits_Pool, how="right", on=['HitID'])
            self.RecHits=_Rec_Hits_Pool
            # checkpoint_2=datetime.datetime.now()
            # print(checkpoint_2-checkpoint_1)
      def TestKalmanHits(self,FEDRAdata_list,MCdata_list):
          import pandas as pd
          _Tot_Hits_df=pd.DataFrame(self.ClusterHits, columns = ['HitID','x','y','z','tx','ty'])[['HitID','z']]
          _Tot_Hits_df["z"] = pd.to_numeric(_Tot_Hits_df["z"],downcast='float')

          _MCClusterHits=[]
          _FEDRAClusterHits=[]
          StatFakeValues=[]
          StatTruthValues=[]
          StatLabels=['Initial # of combinations','Delete self-permutations','Enforce positive directionality','Fedra Track Reconstruction']
          for s in MCdata_list:
             if s[1]>=self.ClusterID[0]*self.Step[0] and s[1]<((self.ClusterID[0]+1)*self.Step[0]):
                    if s[2]>=self.ClusterID[1]*self.Step[1] and s[2]<((self.ClusterID[1]+1)*self.Step[1]):
                        if s[3]>=self.ClusterID[2]*self.Step[2] and s[3]<((self.ClusterID[2]+1)*self.Step[2]):
                           _MCClusterHits.append([s[0],s[6]])
          for s in FEDRAdata_list:
             if s[1]>=self.ClusterID[0]*self.Step[0] and s[1]<((self.ClusterID[0]+1)*self.Step[0]):
                    if s[2]>=self.ClusterID[1]*self.Step[1] and s[2]<((self.ClusterID[1]+1)*self.Step[1]):
                        if s[3]>=self.ClusterID[2]*self.Step[2] and s[3]<((self.ClusterID[2]+1)*self.Step[2]):
                           _FEDRAClusterHits.append([s[0],s[6]])
          #Preparing Raw and MC combined data 1
          _l_MCHits=pd.DataFrame(_MCClusterHits, columns = ['l_HitID','l_MC_ID'])
          _r_MCHits=pd.DataFrame(_MCClusterHits, columns = ['r_HitID','r_MC_ID'])
          _l_FHits=pd.DataFrame(_FEDRAClusterHits, columns = ['l_HitID','l_FEDRA_ID'])
          _r_FHits=pd.DataFrame(_FEDRAClusterHits, columns = ['r_HitID','r_FEDRA_ID'])
          _l_Hits=_Tot_Hits_df.rename(columns={"z": "l_z","HitID": "l_HitID" })
          _r_Hits=_Tot_Hits_df.rename(columns={"z": "r_z","HitID": "r_HitID" })
          #Join hits + MC truth
          _l_Tot_Hits=pd.merge(_l_MCHits, _l_Hits, how="right", on=['l_HitID'])
          _r_Tot_Hits=pd.merge(_r_MCHits, _r_Hits, how="right", on=['r_HitID'])
          _l_Tot_Hits=pd.merge(_l_FHits, _l_Tot_Hits, how="right", on=['l_HitID'])
          _r_Tot_Hits=pd.merge(_r_FHits, _r_Tot_Hits, how="right", on=['r_HitID'])
          _l_Tot_Hits['join_key'] = 'join_key'
          _r_Tot_Hits['join_key'] = 'join_key'
          _Tot_Hits=pd.merge(_l_Tot_Hits, _r_Tot_Hits, how="inner", on=["join_key"])
          _Tot_Hits.l_MC_ID= _Tot_Hits.l_MC_ID.fillna(_Tot_Hits.l_HitID)
          _Tot_Hits.r_MC_ID= _Tot_Hits.r_MC_ID.fillna(_Tot_Hits.r_HitID)
          _Tot_Hits=_Tot_Hits.drop(['join_key'], axis=1)
          StatFakeValues.append(len(_Tot_Hits.axes[0])-len(_Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['l_MC_ID'] != _Tot_Hits['r_MC_ID']]).axes[0]))
          StatTruthValues.append(len(_Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['l_MC_ID'] != _Tot_Hits['r_MC_ID']]).axes[0]))

          _Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['l_HitID'] == _Tot_Hits['r_HitID']], inplace = True)
          StatFakeValues.append(len(_Tot_Hits.axes[0])-len(_Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['l_MC_ID'] != _Tot_Hits['r_MC_ID']]).axes[0]))
          StatTruthValues.append(len(_Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['l_MC_ID'] != _Tot_Hits['r_MC_ID']]).axes[0]))

          _Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['l_z'] <= _Tot_Hits['r_z']], inplace = True)
          StatFakeValues.append(len(_Tot_Hits.axes[0])-len(_Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['l_MC_ID'] != _Tot_Hits['r_MC_ID']]).axes[0]))
          StatTruthValues.append(len(_Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['l_MC_ID'] != _Tot_Hits['r_MC_ID']]).axes[0]))

          _Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['r_FEDRA_ID'] != _Tot_Hits['l_FEDRA_ID']], inplace = True)
          StatFakeValues.append(len(_Tot_Hits.axes[0])-len(_Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['l_MC_ID'] != _Tot_Hits['r_MC_ID']]).axes[0]))
          StatTruthValues.append(len(_Tot_Hits.drop(_Tot_Hits.index[_Tot_Hits['l_MC_ID'] != _Tot_Hits['r_MC_ID']]).axes[0]))
          self.KalmanRecStats=[StatLabels,StatFakeValues,StatTruthValues]
      @staticmethod
      def GenerateLinks(_input,_ClusterID):
          _Top=[]
          _Bottom=[]
          for ip in _input:
              _Top.append(_ClusterID.index(ip[0]))
              _Bottom.append(_ClusterID.index(ip[1]))
          return [_Top,_Bottom]
      def GenerateEdgeAttributes(_input):
          _EdgeAttr=[]
          for ip in _input:
              _EdgeAttr.append(ip[3:])
          return _EdgeAttr
      def GenerateEdgeLabels(_input):
          _EdgeLbl=[]
          for ip in _input:
              _EdgeLbl.append(ip[2])
          return _EdgeLbl
      def UnloadClusterGraph(self):
          del self.ClusterGraph
          del self.HitLinks

      def InjectHit(Predator,Prey, Soft):
          if Soft==False:
             OverlapDetected=False
             New_Predator=copy.deepcopy(Predator)
             for el in range (len(Prey[0])):
                 if Prey[0][el]!='_' and Predator[0][el]!='_' and Prey[0][el]==Predator[0][el]:
                    OverlapDetected=True
                    New_Predator[1][el]+=Prey[1][el]
                 elif Prey[0][el]!='_' and Predator[0][el]!='_' and Prey[0][el]!=Predator[0][el]:
                     return(Predator,False)
                 elif Predator[0][el]=='_' and Prey[0][el]!=Predator[0][el]:
                     New_Predator[0][el]=Prey[0][el]
                     New_Predator[1][el]+=Prey[1][el]
             if OverlapDetected:
                return(New_Predator,True)
             else:
                return(Predator,False)
          if Soft==True:
             for el1 in Prey[0]:
                 for el2 in Predator:
                  if el1==el2:
                     return True
             return False

class EMO:
      def __init__(self,parts):
          self.Header=sorted(parts, key=str.lower)
          self.Partition=len(self.Header)
      def __eq__(self, other):
        return ('-'.join(self.Header)) == ('-'.join(other.Header))
      def __hash__(self):
        return hash(('-'.join(self.Header)))
      def Decorate(self,RawHits): #Decorate hit information
          self.Hits=[]
          for s in range(len(self.Header)):
              self.Hits.append([])
              for t in RawHits:
                   if self.Header[s]==t[5]:
                      self.Hits[s].append(t[:5])
          for Hit in range(0, len(self.Hits)):
             self.Hits[Hit]=sorted(self.Hits[Hit],key=lambda x: float(x[2]),reverse=False)
      def LabelSeed(self,label):
          self.Label=label
      def GetTrInfo(self):
          if hasattr(self,'Hits'):
             if self.Partition==2:
                __XZ1=EMO.GetEquationOfTrack(self.Hits[0])[0]
                __XZ2=EMO.GetEquationOfTrack(self.Hits[1])[0]
                __YZ1=EMO.GetEquationOfTrack(self.Hits[0])[1]
                __YZ2=EMO.GetEquationOfTrack(self.Hits[1])[1]
                __X1S=EMO.GetEquationOfTrack(self.Hits[0])[3]
                __X2S=EMO.GetEquationOfTrack(self.Hits[1])[3]
                __Y1S=EMO.GetEquationOfTrack(self.Hits[0])[4]
                __Y2S=EMO.GetEquationOfTrack(self.Hits[1])[4]
                __Z1S=EMO.GetEquationOfTrack(self.Hits[0])[5]
                __Z2S=EMO.GetEquationOfTrack(self.Hits[1])[5]
                __vector_1_st = np.array([np.polyval(__XZ1,self.Hits[0][0][2]),np.polyval(__YZ1,self.Hits[0][0][2]),self.Hits[0][0][2]])
                __vector_1_end = np.array([np.polyval(__XZ1,self.Hits[0][len(self.Hits[0])-1][2]),np.polyval(__YZ1,self.Hits[0][len(self.Hits[0])-1][2]),self.Hits[0][len(self.Hits[0])-1][2]])
                __vector_2_st = np.array([np.polyval(__XZ2,self.Hits[0][0][2]),np.polyval(__YZ2,self.Hits[0][0][2]),self.Hits[0][0][2]])
                __vector_2_end = np.array([np.polyval(__XZ2,self.Hits[0][len(self.Hits[0])-1][2]),np.polyval(__YZ2,self.Hits[0][len(self.Hits[0])-1][2]),self.Hits[0][len(self.Hits[0])-1][2]])
                __result=EMO.closestDistanceBetweenLines(__vector_1_st,__vector_1_end,__vector_2_st,__vector_2_end,clampAll=False,clampA0=False,clampA1=False,clampB0=False,clampB1=False)
                __midpoint=(__result[0]+__result[1])/2
                __v1=np.subtract(__vector_1_end,__midpoint)
                __v2=np.subtract(__vector_2_end,__midpoint)
                if self.Hits[0][len(self.Hits)-1][2]>self.Hits[1][len(self.Hits)-1][2]: #Workout which track is leading (has highest z-coordinate)
                    __leading_seg=0
                    __subleading_seg=1
                else:
                    __leading_seg=1
                    __subleading_seg=0
                self.Opening_Angle=EMO.angle_between(__v1, __v2)
                self.DOCA=__result[2]
                self.SLG=float(self.Hits[__leading_seg][0][2])-float(self.Hits[__subleading_seg][len(self.Hits[__subleading_seg])-1][2])
                __x2=float(self.Hits[__leading_seg][0][0])
                __x1=self.Hits[__subleading_seg][len(self.Hits[__subleading_seg])-1][0]
                __y2=float(self.Hits[__leading_seg][0][1])
                __y1=self.Hits[__subleading_seg][len(self.Hits[__subleading_seg])-1][1]
                self.STG=math.sqrt(((__x2-__x1)**2)+((__y2-__y1)**2))
             else:
                 raise ValueError("Method 'DecorateTrackGeoInfo' currently works for seeds with partition of 2 only")
          else:
                raise ValueError("Method 'DecorateTrackGeoInfo' works only if 'Decorate' method has been acted upon the seed before")
      def TrackQualityCheck(self,MaxDoca,MaxSLG, MaxSTG,MaxAngle):
                    return (self.DOCA<=MaxDoca and self.SLG<=MaxSLG and self.STG<=(MaxSTG+(self.SLG*0.96)) and abs(self.Opening_Angle)<=MaxAngle)
      @staticmethod
      def unit_vector(vector):
          return vector / np.linalg.norm(vector)

      def angle_between(v1, v2):
            v1_u = EMO.unit_vector(v1)
            v2_u = EMO.unit_vector(v2)
            dot = v1_u[0]*v2_u[0] + v1_u[1]*v2_u[1]      # dot product
            det = v1_u[0]*v2_u[1] - v1_u[1]*v2_u[0]      # determinant
            return np.arctan2(det, dot)

      def GetEquationOfTrack(EMO):
          Xval=[]
          Yval=[]
          Zval=[]
          for Hits in EMO:
              Xval.append(Hits[0])
              Yval.append(Hits[1])
              Zval.append(Hits[2])
          XZ=np.polyfit(Zval,Xval,1)
          YZ=np.polyfit(Zval,Yval,1)
          return (XZ,YZ, 'N/A',Xval[0],Yval[0],Zval[0])

      def closestDistanceBetweenLines(a0,a1,b0,b1,clampAll=False,clampA0=False,clampA1=False,clampB0=False,clampB1=False):
            a0=np.array(a0)
            a1=np.array(a1)
            b0=np.array(b0)
            b1=np.array(b1)
            # If clampAll=True, set all clamps to True
            if clampAll:
                clampA0=True
                clampA1=True
                clampB0=True
                clampB1=True


            # Calculate denomitator
            A = a1 - a0
            B = b1 - b0
            magA = np.linalg.norm(A)
            magB = np.linalg.norm(B)

            _A = A / magA
            _B = B / magB

            cross = np.cross(_A, _B);
            denom = np.linalg.norm(cross)**2


            # If lines are parallel (denom=0) test if lines overlap.
            # If they don't overlap then there is a closest point solution.
            # If they do overlap, there are infinite closest positions, but there is a closest distance
            if not denom:
                d0 = np.dot(_A,(b0-a0))

                # Overlap only possible with clamping
                if clampA0 or clampA1 or clampB0 or clampB1:
                    d1 = np.dot(_A,(b1-a0))

                    # Is segment B before A?
                    if d0 <= 0 >= d1:
                        if clampA0 and clampB1:
                            if np.absolute(d0) < np.absolute(d1):
                                return a0,b0,np.linalg.norm(a0-b0)
                            return a0,b1,np.linalg.norm(a0-b1)


                    # Is segment B after A?
                    elif d0 >= magA <= d1:
                        if clampA1 and clampB0:
                            if np.absolute(d0) < np.absolute(d1):
                                return a1,b0,np.linalg.norm(a1-b0)
                            return a1,b1,np.linalg.norm(a1-b1)


                # Segments overlap, return distance between parallel segments
                return None,None,np.linalg.norm(((d0*_A)+a0)-b0)



            # Lines criss-cross: Calculate the projected closest points
            t = (b0 - a0);
            detA = np.linalg.det([t, _B, cross])
            detB = np.linalg.det([t, _A, cross])

            t0 = detA/denom;
            t1 = detB/denom;

            pA = a0 + (_A * t0) # Projected closest point on segment A
            pB = b0 + (_B * t1) # Projected closest point on segment B


            # Clamp projections
            if clampA0 or clampA1 or clampB0 or clampB1:
                if clampA0 and t0 < 0:
                    pA = a0
                elif clampA1 and t0 > magA:
                    pA = a1

                if clampB0 and t1 < 0:
                    pB = b0
                elif clampB1 and t1 > magB:
                    pB = b1

                # Clamp projection A
                if (clampA0 and t0 < 0) or (clampA1 and t0 > magA):
                    dot = np.dot(_B,(pA-b0))
                    if clampB0 and dot < 0:
                        dot = 0
                    elif clampB1 and dot > magB:
                        dot = magB
                    pB = b0 + (_B * dot)

                # Clamp projection B
                if (clampB0 and t1 < 0) or (clampB1 and t1 > magB):
                    dot = np.dot(_A,(pB-a0))
                    if clampA0 and dot < 0:
                        dot = 0
                    elif clampA1 and dot > magA:
                        dot = magA
                    pA = a0 + (_A * dot)
            return pA,pB,np.linalg.norm(pA-pB)
      

def GenerateModel(ModelMeta):
      if ModelMeta.ModelFramework=='PyTorch':
         import torch
         import torch.nn as nn
         from torch.nn import Sequential as Seq, Linear, ReLU, Sigmoid
         from torch import Tensor
         import torch_geometric
         from torch_geometric.nn import MessagePassing
         from MH_IN import InteractionNetwork as IN
         if ModelMeta.ModelArchitecture=='TCN':
            class MLP(nn.Module):
                  def __init__(self, input_size, output_size, hidden_size):
                     super(MLP, self).__init__()

                     if ModelMeta.ModelParameters[0]==3:
                         self.layers = nn.Sequential(
                             nn.Linear(input_size, hidden_size),
                             nn.ReLU(),
                             nn.Linear(hidden_size, hidden_size),
                             nn.ReLU(),
                             nn.Linear(hidden_size, hidden_size),
                             nn.ReLU(),
                             nn.Linear(hidden_size, output_size),
                         )
                     elif ModelMeta.ModelParameters[0]==4:
                         self.layers = nn.Sequential(
                             nn.Linear(input_size, hidden_size),
                             nn.ReLU(),
                             nn.Linear(hidden_size, hidden_size),
                             nn.ReLU(),
                             nn.Linear(hidden_size, hidden_size),
                             nn.ReLU(),
                             nn.Linear(hidden_size, hidden_size),
                             nn.ReLU(),
                             nn.Linear(hidden_size, output_size),
                         )

                     elif ModelMeta.ModelParameters[0]==5:
                         self.layers = nn.Sequential(
                             nn.Linear(input_size, hidden_size),
                             nn.ReLU(),
                             nn.Linear(hidden_size, hidden_size),
                             nn.ReLU(),
                             nn.Linear(hidden_size, hidden_size),
                             nn.ReLU(),
                             nn.Linear(hidden_size, hidden_size),
                             nn.ReLU(),
                             nn.Linear(hidden_size, hidden_size),
                             nn.ReLU(),
                             nn.Linear(hidden_size, output_size),
                         )

                     elif ModelMeta.ModelParameters[0]==6:
                         self.layers = nn.Sequential(
                             nn.Linear(input_size, hidden_size),
                             nn.ReLU(),
                             nn.Linear(hidden_size, hidden_size),
                             nn.ReLU(),
                             nn.Linear(hidden_size, hidden_size),
                             nn.ReLU(),
                             nn.Linear(hidden_size, hidden_size),
                             nn.ReLU(),
                             nn.Linear(hidden_size, hidden_size),
                             nn.ReLU(),
                             nn.Linear(hidden_size, hidden_size),
                             nn.ReLU(),
                             nn.Linear(hidden_size, output_size),
                         )

                     elif ModelMeta.ModelParameters[0]==7:
                         self.layers = nn.Sequential(
                             nn.Linear(input_size, hidden_size),
                             nn.ReLU(),
                             nn.Linear(hidden_size, hidden_size),
                             nn.ReLU(),
                             nn.Linear(hidden_size, hidden_size),
                             nn.ReLU(),
                             nn.Linear(hidden_size, hidden_size),
                             nn.ReLU(),
                             nn.Linear(hidden_size, hidden_size),
                             nn.ReLU(),
                             nn.Linear(hidden_size, hidden_size),
                             nn.ReLU(),
                             nn.Linear(hidden_size, hidden_size),
                             nn.ReLU(),
                             nn.Linear(hidden_size, output_size),
                         )

                     elif ModelMeta.ModelParameters[0]==8:
                         self.layers = nn.Sequential(
                             nn.Linear(input_size, hidden_size),
                             nn.ReLU(),
                             nn.Linear(hidden_size, hidden_size),
                             nn.ReLU(),
                             nn.Linear(hidden_size, hidden_size),
                             nn.ReLU(),
                             nn.Linear(hidden_size, hidden_size),
                             nn.ReLU(),
                             nn.Linear(hidden_size, hidden_size),
                             nn.ReLU(),
                             nn.Linear(hidden_size, hidden_size),
                             nn.ReLU(),
                             nn.Linear(hidden_size, hidden_size),
                             nn.ReLU(),
                             nn.Linear(hidden_size, hidden_size),
                             nn.ReLU(),
                             nn.Linear(hidden_size, output_size),
                         )

                     elif ModelMeta.ModelParameters[0]==2:
                         self.layers = nn.Sequential(
                             nn.Linear(input_size, hidden_size),
                             nn.ReLU(),
                             nn.Linear(hidden_size, hidden_size),
                             nn.ReLU(),
                             nn.Linear(hidden_size, output_size),
                         )
                     elif ModelMeta.ModelParameters[0]==1:
                         self.layers = nn.Sequential(
                             nn.Linear(input_size, hidden_size),
                             nn.ReLU(),
                             nn.Linear(hidden_size, output_size),
                         )
                  def forward(self, C):
                     return self.layers(C)

            class TCN(nn.Module):
                 def __init__(self, node_indim, edge_indim, hs):
                     super(TCN, self).__init__()
                     if ModelMeta.ModelParameters[2]==2:
                         self.in_w1 = IN(node_indim, edge_indim,
                                         node_outdim=node_indim, edge_outdim=edge_indim,
                                         hidden_size=hs)
                         self.in_w2 = IN(node_indim, edge_indim,
                                         node_outdim=node_indim, edge_outdim=edge_indim,
                                         hidden_size=hs)

                     elif ModelMeta.ModelParameters[2]==1:
                         self.in_w1 = IN(node_indim, edge_indim,
                                         node_outdim=node_indim, edge_outdim=edge_indim,
                                         hidden_size=hs)

                     elif ModelMeta.ModelParameters[2]==3:
                         self.in_w1 = IN(node_indim, edge_indim,
                                         node_outdim=node_indim, edge_outdim=edge_indim,
                                         hidden_size=hs)
                         self.in_w2 = IN(node_indim, edge_indim,
                                         node_outdim=node_indim, edge_outdim=edge_indim,
                                         hidden_size=hs)
                         self.in_w3 = IN(node_indim, edge_indim,
                                         node_outdim=node_indim, edge_outdim=edge_indim,
                                         hidden_size=hs)

                     elif ModelMeta.ModelParameters[2]==4:
                         self.in_w1 = IN(node_indim, edge_indim,
                                         node_outdim=node_indim, edge_outdim=edge_indim,
                                         hidden_size=hs)
                         self.in_w2 = IN(node_indim, edge_indim,
                                         node_outdim=node_indim, edge_outdim=edge_indim,
                                         hidden_size=hs)
                         self.in_w3 = IN(node_indim, edge_indim,
                                         node_outdim=node_indim, edge_outdim=edge_indim,
                                         hidden_size=hs)
                         self.in_w4 = IN(node_indim, edge_indim,
                                         node_outdim=node_indim, edge_outdim=edge_indim,
                                         hidden_size=hs)
                     elif ModelMeta.ModelParameters[2]==5:
                         self.in_w1 = IN(node_indim, edge_indim,
                                         node_outdim=node_indim, edge_outdim=edge_indim,
                                         hidden_size=hs)
                         self.in_w2 = IN(node_indim, edge_indim,
                                         node_outdim=node_indim, edge_outdim=edge_indim,
                                         hidden_size=hs)
                         self.in_w3 = IN(node_indim, edge_indim,
                                         node_outdim=node_indim, edge_outdim=edge_indim,
                                         hidden_size=hs)
                         self.in_w4 = IN(node_indim, edge_indim,
                                         node_outdim=node_indim, edge_outdim=edge_indim,
                                         hidden_size=hs)
                         self.in_w5 = IN(node_indim, edge_indim,
                                         node_outdim=node_indim, edge_outdim=edge_indim,
                                         hidden_size=hs)
                     elif ModelMeta.ModelParameters[2]==6:
                         self.in_w1 = IN(node_indim, edge_indim,
                                         node_outdim=node_indim, edge_outdim=edge_indim,
                                         hidden_size=hs)
                         self.in_w2 = IN(node_indim, edge_indim,
                                         node_outdim=node_indim, edge_outdim=edge_indim,
                                         hidden_size=hs)
                         self.in_w3 = IN(node_indim, edge_indim,
                                         node_outdim=node_indim, edge_outdim=edge_indim,
                                         hidden_size=hs)
                         self.in_w4 = IN(node_indim, edge_indim,
                                         node_outdim=node_indim, edge_outdim=edge_indim,
                                         hidden_size=hs)
                         self.in_w5 = IN(node_indim, edge_indim,
                                         node_outdim=node_indim, edge_outdim=edge_indim,
                                         hidden_size=hs)
                         self.in_w6 = IN(node_indim, edge_indim,
                                         node_outdim=node_indim, edge_outdim=edge_indim,
                                         hidden_size=hs)
                     elif ModelMeta.ModelParameters[2]==7:
                         self.in_w1 = IN(node_indim, edge_indim,
                                         node_outdim=node_indim, edge_outdim=edge_indim,
                                         hidden_size=hs)
                         self.in_w2 = IN(node_indim, edge_indim,
                                         node_outdim=node_indim, edge_outdim=edge_indim,
                                         hidden_size=hs)
                         self.in_w3 = IN(node_indim, edge_indim,
                                         node_outdim=node_indim, edge_outdim=edge_indim,
                                         hidden_size=hs)
                         self.in_w4 = IN(node_indim, edge_indim,
                                         node_outdim=node_indim, edge_outdim=edge_indim,
                                         hidden_size=hs)
                         self.in_w5 = IN(node_indim, edge_indim,
                                         node_outdim=node_indim, edge_outdim=edge_indim,
                                         hidden_size=hs)
                         self.in_w6 = IN(node_indim, edge_indim,
                                         node_outdim=node_indim, edge_outdim=edge_indim,
                                         hidden_size=hs)
                         self.in_w7 = IN(node_indim, edge_indim,
                                         node_outdim=node_indim, edge_outdim=edge_indim,
                                         hidden_size=hs)
                     elif ModelMeta.ModelParameters[2]==8:
                         self.in_w1 = IN(node_indim, edge_indim,
                                         node_outdim=node_indim, edge_outdim=edge_indim,
                                         hidden_size=hs)
                         self.in_w2 = IN(node_indim, edge_indim,
                                         node_outdim=node_indim, edge_outdim=edge_indim,
                                         hidden_size=hs)
                         self.in_w3 = IN(node_indim, edge_indim,
                                         node_outdim=node_indim, edge_outdim=edge_indim,
                                         hidden_size=hs)
                         self.in_w4 = IN(node_indim, edge_indim,
                                         node_outdim=node_indim, edge_outdim=edge_indim,
                                         hidden_size=hs)
                         self.in_w5 = IN(node_indim, edge_indim,
                                         node_outdim=node_indim, edge_outdim=edge_indim,
                                         hidden_size=hs)
                         self.in_w6 = IN(node_indim, edge_indim,
                                         node_outdim=node_indim, edge_outdim=edge_indim,
                                         hidden_size=hs)
                         self.in_w7 = IN(node_indim, edge_indim,
                                         node_outdim=node_indim, edge_outdim=edge_indim,
                                         hidden_size=hs)
                         self.in_w8 = IN(node_indim, edge_indim,
                                         node_outdim=node_indim, edge_outdim=edge_indim,
                                         hidden_size=hs)

                     self.W = MLP(edge_indim*(ModelMeta.ModelParameters[2]+1), 1, ModelMeta.ModelParameters[1])

                 def forward(self, x: Tensor, edge_index: Tensor,
                             edge_attr: Tensor) -> Tensor:

                     # re-embed the graph twice with add aggregation
                     if ModelMeta.ModelParameters[2]==2:
                         x1, edge_attr_1 = self.in_w1(x, edge_index, edge_attr)

                         x2, edge_attr_2 = self.in_w2(x1, edge_index, edge_attr_1)

                         # combine all edge features, use to predict edge weights
                         initial_edge_attr = torch.cat([edge_attr, edge_attr_1,
                                                        edge_attr_2], dim=1)
                     if ModelMeta.ModelParameters[2]==3:
                         x1, edge_attr_1 = self.in_w1(x, edge_index, edge_attr)

                         x2, edge_attr_2 = self.in_w2(x1, edge_index, edge_attr_1)

                         x3, edge_attr_3 = self.in_w3(x2, edge_index, edge_attr_2)

                         # combine all edge features, use to predict edge weights
                         initial_edge_attr = torch.cat([edge_attr, edge_attr_1,
                                                        edge_attr_2, edge_attr_3], dim=1)
                     if ModelMeta.ModelParameters[2]==4:
                         x1, edge_attr_1 = self.in_w1(x, edge_index, edge_attr)

                         x2, edge_attr_2 = self.in_w2(x1, edge_index, edge_attr_1)

                         x3, edge_attr_3 = self.in_w3(x2, edge_index, edge_attr_2)

                         x4, edge_attr_4 = self.in_w4(x3, edge_index, edge_attr_3)

                         # combine all edge features, use to predict edge weights
                         initial_edge_attr = torch.cat([edge_attr, edge_attr_1,
                                                        edge_attr_2, edge_attr_3, edge_attr_4], dim=1)

                     if ModelMeta.ModelParameters[2]==5:
                         x1, edge_attr_1 = self.in_w1(x, edge_index, edge_attr)

                         x2, edge_attr_2 = self.in_w2(x1, edge_index, edge_attr_1)

                         x3, edge_attr_3 = self.in_w3(x2, edge_index, edge_attr_2)

                         x4, edge_attr_4 = self.in_w4(x3, edge_index, edge_attr_3)

                         x5, edge_attr_5 = self.in_w5(x4, edge_index, edge_attr_4)

                         # combine all edge features, use to predict edge weights
                         initial_edge_attr = torch.cat([edge_attr, edge_attr_1,
                                                        edge_attr_2, edge_attr_3, edge_attr_4,edge_attr_5], dim=1)

                     if ModelMeta.ModelParameters[2]==6:
                         x1, edge_attr_1 = self.in_w1(x, edge_index, edge_attr)

                         x2, edge_attr_2 = self.in_w2(x1, edge_index, edge_attr_1)

                         x3, edge_attr_3 = self.in_w3(x2, edge_index, edge_attr_2)

                         x4, edge_attr_4 = self.in_w4(x3, edge_index, edge_attr_3)

                         x5, edge_attr_5 = self.in_w5(x4, edge_index, edge_attr_4)

                         x6, edge_attr_6 = self.in_w6(x5, edge_index, edge_attr_5)

                         # combine all edge features, use to predict edge weights
                         initial_edge_attr = torch.cat([edge_attr, edge_attr_1,
                                                        edge_attr_2, edge_attr_3, edge_attr_4,edge_attr_5,edge_attr_6], dim=1)
                     if ModelMeta.ModelParameters[2]==7:
                         x1, edge_attr_1 = self.in_w1(x, edge_index, edge_attr)

                         x2, edge_attr_2 = self.in_w2(x1, edge_index, edge_attr_1)

                         x3, edge_attr_3 = self.in_w3(x2, edge_index, edge_attr_2)

                         x4, edge_attr_4 = self.in_w4(x3, edge_index, edge_attr_3)

                         x5, edge_attr_5 = self.in_w5(x4, edge_index, edge_attr_4)

                         x6, edge_attr_6 = self.in_w6(x5, edge_index, edge_attr_5)

                         x7, edge_attr_7 = self.in_w7(x6, edge_index, edge_attr_6)

                         # combine all edge features, use to predict edge weights
                         initial_edge_attr = torch.cat([edge_attr, edge_attr_1,
                                                        edge_attr_2, edge_attr_3, edge_attr_4,edge_attr_5,edge_attr_6,edge_attr_7], dim=1)
                     if ModelMeta.ModelParameters[2]==8:
                         x1, edge_attr_1 = self.in_w1(x, edge_index, edge_attr)

                         x2, edge_attr_2 = self.in_w2(x1, edge_index, edge_attr_1)

                         x3, edge_attr_3 = self.in_w3(x2, edge_index, edge_attr_2)

                         x4, edge_attr_4 = self.in_w4(x3, edge_index, edge_attr_3)

                         x5, edge_attr_5 = self.in_w5(x4, edge_index, edge_attr_4)

                         x6, edge_attr_6 = self.in_w6(x5, edge_index, edge_attr_5)

                         x7, edge_attr_7 = self.in_w7(x6, edge_index, edge_attr_6)

                         x8, edge_attr_8 = self.in_w8(x7, edge_index, edge_attr_7)

                         # combine all edge features, use to predict edge weights
                         initial_edge_attr = torch.cat([edge_attr, edge_attr_1,
                                                        edge_attr_2, edge_attr_3, edge_attr_4,edge_attr_5,edge_attr_6,edge_attr_7,edge_attr_8], dim=1)

                     if ModelMeta.ModelParameters[2]==1:
                         x1, edge_attr_1 = self.in_w1(x, edge_index, edge_attr)
                         # combine all edge features, use to predict edge weights
                         initial_edge_attr = torch.cat([edge_attr, edge_attr_1], dim=1)
                     edge_weights = torch.sigmoid(self.W(initial_edge_attr))
                     return edge_weights
            model = TCN(ModelMeta.num_node_features, ModelMeta.num_edge_features, ModelMeta.ModelParameters[3])
            return model


def CleanFolder(folder,key):
    if key=='':
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)
    else:
      for the_file in os.listdir(folder):
                file_path=os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path) and (key in the_file):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)
#This function automates csv read/write operations
def LogOperations(flocation,mode, message):
    if mode=='a':
        csv_writer_log=open(flocation,"a")
        log_writer = csv.writer(csv_writer_log)
        if len(message)>0:
         for m in message:
          log_writer.writerow(m)
        csv_writer_log.close()
    if mode=='w':
        csv_writer_log=open(flocation,"w")
        log_writer = csv.writer(csv_writer_log)
        if len(message)>0:
         for m in message:
           log_writer.writerow(m)
        csv_writer_log.close()
    if mode=='r':
        csv_reader_log=open(flocation,"r")
        log_reader = csv.reader(csv_reader_log)
        return list(log_reader)


def PickleOperations(flocation,mode, message):
    import pickle
    if mode=='w':
        pickle_writer_log=open(flocation,"wb")
        pickle.dump(message, pickle_writer_log)
        pickle_writer_log.close()
        return ('',"UF.PickleOperations Message: Data has been written successfully into "+flocation)
    if mode=='r':
        pickle_writer_log=open(flocation,'rb')
        result=pickle.load(pickle_writer_log)
        pickle_writer_log.close()
        return (result,"UF.PickleOperations Message: Data has been loaded successfully from "+flocation)

def RecCleanUp(AFS_DIR, EOS_DIR, Process, FileNames, ProcessId):
      subprocess.call(['condor_rm', '-constraint', ProcessId])
      EOSsubDIR=EOS_DIR+'/'+'ANNADEA'
      EOSsubModelDIR=EOSsubDIR+'/'+'Data/REC_SET'
      folder =  EOSsubModelDIR
      for f in FileNames:
          CleanFolder(folder,f)
      folder =  AFS_DIR+'/HTCondor/SH'
      CleanFolder(folder,'SH_'+Process+'_')
      folder =  AFS_DIR+'/HTCondor/SUB'
      CleanFolder(folder,'SUB_'+Process+'_')
      folder =  AFS_DIR+'/HTCondor/MSG'
      CleanFolder(folder,'MSG_'+Process+'_')

def EvalCleanUp(AFS_DIR, EOS_DIR, Process, FileNames, ProcessId):
      subprocess.call(['condor_rm', '-constraint', ProcessId])
      EOSsubDIR=EOS_DIR+'/'+'ANNADEA'
      EOSsubModelDIR=EOSsubDIR+'/'+'Data/TEST_SET'
      folder =  EOSsubModelDIR
      for f in FileNames:
          CleanFolder(folder,f)
      folder =  AFS_DIR+'/HTCondor/SH'
      CleanFolder(folder,'SH_'+Process+'_')
      folder =  AFS_DIR+'/HTCondor/SUB'
      CleanFolder(folder,'SUB_'+Process+'_')
      folder =  AFS_DIR+'/HTCondor/MSG'
      CleanFolder(folder,'MSG_'+Process+'_')

def TrainCleanUp(AFS_DIR, EOS_DIR, Process, FileNames, ProcessId):
      subprocess.call(['condor_rm', '-constraint', ProcessId])
      EOSsubDIR=EOS_DIR+'/'+'ANNADEA'
      EOSsubModelDIR=EOSsubDIR+'/'+'Data/TRAIN_SET'
      folder =  EOSsubModelDIR
      for f in FileNames:
          CleanFolder(folder,f)
      EOSsubModelDIR=EOSsubDIR+'/'+'Models'
      folder =  EOSsubModelDIR
      for f in FileNames:
          CleanFolder(folder,f)
      folder =  AFS_DIR+'/HTCondor/SH'
      CleanFolder(folder,'SH_'+Process+'_')
      folder =  AFS_DIR+'/HTCondor/SUB'
      CleanFolder(folder,'SUB_'+Process+'_')
      folder =  AFS_DIR+'/HTCondor/MSG'
      CleanFolder(folder,'MSG_'+Process+'_')

def SubmitJobs2Condor(job):
    SHName = job[2]
    SUBName = job[3]
    if job[8]:
        MSGName=job[4]
    OptionLine = job[0][0]+str(job[1][0])
    for line in range(1,len(job[0])):
        OptionLine+=job[0][line]
        OptionLine+=str(job[1][line])
    f = open(SUBName, "w")
    f.write("executable = " + SHName)
    f.write("\n")
    if job[8]:
        f.write("output ="+MSGName+".out")
        f.write("\n")
        f.write("error ="+MSGName+".err")
        f.write("\n")
        f.write("log ="+MSGName+".log")
        f.write("\n")
    f.write('requirements = (CERNEnvironment =!= "qa")')
    f.write("\n")
    if job[9]:
        f.write('request_gpus = 1')
        f.write("\n")
    f.write('arguments = $(Process)')
    f.write("\n")
    f.write('+SoftUsed = '+'"'+job[7]+'"')
    f.write("\n")
    f.write('transfer_output_files = ""')
    f.write("\n")
    f.write('+JobFlavour = "workday"')
    f.write("\n")
    f.write('queue ' + str(job[6]))
    f.write("\n")
    f.close()
    TotalLine = 'python3 ' + job[5] + OptionLine
    f = open(SHName, "w")
    f.write("#!/bin/bash")
    f.write("\n")
    f.write("set -ux")
    f.write("\n")
    f.write(TotalLine)
    f.write("\n")
    f.close()
    subprocess.call(['condor_submit', SUBName])
    print(TotalLine, " has been successfully submitted")

def ErrorOperations(a,b,a_e,b_e,mode):
    if mode=='+' or mode == '-':
        c_e=math.sqrt((a_e**2) + (b_e**2))
        return(c_e)
    if mode=='*':
        c_e=a*b*math.sqrt(((a_e/a)**2) + ((b_e/b)**2))
        return(c_e)
    if mode=='/':
        c_e=(a/b)*math.sqrt(((a_e/a)**2) + ((b_e/b)**2))
        return(c_e)
