import os
import sys
import re
import numpy as np

###attention!!! There is some bug in this script!
def usage():
	print "usage:python dtw.py featFile_query featFile_utt";
	print "--featFile_query:file containing the feature(eg. posteriorgram) of query";
	print "--featFile_query:file containing the feature(eg. posteriorgram) of utterance";

	exit();

def readFeat(filePath):
	con=open(filePath).readlines();
	feat=[map(float,one.strip().split()) for one in con];
	return np.array(feat);

def smooth_feat(feat,smooth_param):
	dim=len(feat[0]);
	u=np.ones([len(feat),dim])*(1.0/dim); ###the uniform probability distribution matrix
	smoothed_feat=(1-smooth_param)*feat+smooth_param*u;
	return smoothed_feat;
	

def comput_distance(vec1,vec2):
	distance=-np.log10(np.dot(vec1,vec2));
	return distance;

def compute_simi_matrix(feat_utt,feat_query):
	simi_matrix=-np.log10(np.dot(feat_query,np.transpose(feat_utt)));
	return simi_matrix;
	
def compute_acc_distance(similarity_matrix,acc_distance_begin,begin,end,fai):
	begin_x,begin_y=begin;
	end_x,end_y=end;
	distance_sum=0.0;
	bet_x=end_x-begin_x;
	bet_y=end_y-begin_y;
	gamma=max(bet_x,bet_y);	
	if((begin_x+1)==end_x):
		distance_sum=sum(similarity_matrix[end_x][begin_y+1:end_y+1]);
		#for i in range(begin_y+1,end_y+1):
		#	distance_sum=distance_sum+similarity_matrix[end_x][i];
		distance_sum=float(gamma**fai)/bet_y*distance_sum;
	elif((begin_y+1)==end_y):
		distance_sum=sum(similarity_matrix[begin_x+1:end_x+1,end_y]);	
		#for i in range(begin_x+1,end_x+1):
		#	distance_sum=distance_sum+similarity_matrix[i][end_y];
		distance_sum=float(gamma**fai)*distance_sum;	
	else:
		print "incorrect transition!";
		exit();
	return distance_sum+acc_distance_begin;

def dtw(feat_query,feat_utt,smooth_param,fai):
	num_feat_query=len(feat_query);
	num_feat_utt=len(feat_utt);
	
	###smooth the feats
	smoothed_feat_query=smooth_feat(feat_query,smooth_param);
	smoothed_feat_utt=smooth_feat(feat_utt,smooth_param);	
		
	similarity_matrix=compute_simi_matrix(smoothed_feat_utt,smoothed_feat_query);

	###output the mediate results
	#f1=open("smoothed_query","w");
	#f1.writelines('\n'.join([' '.join(map(str,one)) for one in smoothed_feat_query]));
	#f2=open("smoothed_utt","w");
	#f2.writelines('\n'.join([' '.join(map(str,one)) for one in smoothed_feat_utt]));
	f3=open("similarity","w");
	f3.writelines('\n'.join([' '.join(map(str,one)) for one in similarity_matrix]));

	

	distance_acc=np.ones([num_feat_query,num_feat_utt])*float('inf'); ###initiate the whole accumulating distance matrix as INF 
	paths={}; ###use a dictionay to save the paths(key=beginning point of a path line; value=ending point of the same path line)
	
	###initialization
	for i in range(num_feat_utt):  
		distance_acc[0][i]=similarity_matrix[0][i];	###compute_distance(smoothed_feat_query[0],smoothed_feat_utt[i]); 
	
	for j in range(num_feat_query):  
		distance_acc[j][0]=similarity_matrix[j][0];	###compute_distance(smoothed_feat_query[j],smoothed_feat_utt[0]); 	
	
	###DP step
	for i in range(1,num_feat_query):
		for j in range(1,num_feat_utt):
			candidate={};
			if(i==1 or j==1): ###special case			
				candidate[(0,0)]=compute_acc_distance(similarity_matrix,distance_acc[0][0],(0,0),(i,j),fai);
			for k in range(1,j):
				candidate[(i-1,k)]=compute_acc_distance(similarity_matrix,distance_acc[i-1][k],(i-1,k),(i,j),fai);
			if(j!=1):				
				for k in range(0,i):
					if(candidate.has_key((k,j-1))):
						continue;
					candidate[(k,j-1)]=compute_acc_distance(similarity_matrix,distance_acc[k][j-1],(k,j-1),(i,j),fai);
			
			###sort the candidate transitions and select the best one (with the smallest accumulating distance)
			candidate_sorted=sorted(candidate.items(),key=lambda x:x[1] );
			distance_acc[i][j]=candidate_sorted[0][1];
			paths[(i,j)]=(candidate_sorted[0][0]);
	

	###save the distance_acc
	#f4=open("distance_matrix","w");
	#f4.writelines('\n'.join([' '.join(map(str,one)) for one in distance_acc]));		
		
	
	###search for the best full matching path and its distance
	minDistance=float('inf');
	bestPaths={};	###maybe there exists more than one best paths! key of the dictionay is the best paths' ending point;and the value of the dictionary is the full path
	for i in range(1,num_feat_utt):
		dist=distance_acc[num_feat_query-1][i];
		if(dist<minDistance):
			minDistance=dist;
			#bestPath_end=paths[(num_feat_query-1,i)];
			bestPaths[(num_feat_query-1,i)]=[(num_feat_query-1,i)];
	for key in bestPaths:	
		while(True):
			cur_point=bestPaths[key][-1];
			if(not paths.has_key(cur_point)):
				break;
			pre_point=paths[cur_point];
			bestPaths[key].append(pre_point);
		bestPaths[key].reverse();	
	return minDistance,bestPaths;


def main():
	argc=len(sys.argv);
	if(argc != 3):
		usage();

	featFile_query=sys.argv[1];
	featFile_utt=sys.argv[2];
	feat_query=readFeat(featFile_query); ###feature matrix of query
	feat_utt=readFeat(featFile_utt);     ###feature matrix of utterance
	smooth_param=0.00001;		###parameter value for smoothing
	fai=0;			###parameter value for computing accumulating distance
	[minDistance,bestPath]=dtw(feat_query,feat_utt,smooth_param,fai);
	final_distance=minDistance/len(feat_query);
	#print "Matching over!"
	#print "There exists "+str(len(bestPath))+" best path(s):"
	#for key in bestPath:
	#	print bestPath[key];
	#print "with min distance: "+str(final_distance);

main();

