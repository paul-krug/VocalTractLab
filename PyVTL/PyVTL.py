#####################################################################################################################################################
#---------------------------------------------------------------------------------------------------------------------------------------------------#
#	- This file is a part of the Python module PyVTL, see https://github.com/TUD-STKS/PyVTL
#---------------------------------------------------------------------------------------------------------------------------------------------------#
#
#	- Copyright (C) 2021, Paul Konstantin Krug, Dresden, Germany
#	- https://github.com/TUD-STKS/PyVTL
#	- Author: Paul Konstantin Krug, TU Dresden
#
#	- License:
#
#		This program is free software: you can redistribute it and/or modify
#		it under the terms of the GNU General Public License as published by
#		the Free Software Foundation, either version 3 of the License, or
#		(at your option) any later version.
#		
#		This program is distributed in the hope that it will be useful,
#		but WITHOUT ANY WARRANTY; without even the implied warranty of
#		MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#		GNU General Public License for more details.
#		
#		You should have received a copy of the GNU General Public License
#		along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#---------------------------------------------------------------------------------------------------------------------------------------------------#
#####################################################################################################################################################
#---------------------------------------------------------------------------------------------------------------------------------------------------#
# Requirements:
#	- python 3 (tested with version 3.7)
#	- numpy    (tested with version 1.19.5)
#	- pandas   (tested with version 1.2.1)
#	- scipy    (tested with version 1.6.0)
#---------------------------------------------------------------------------------------------------------------------------------------------------#
#####################################################################################################################################################
#---------------------------------------------------------------------------------------------------------------------------------------------------#
#__all__ = ['a', 'b', 'c']
__version__ = '0.1'
__author__ = 'Paul Konstantin Krug'
#---------------------------------------------------------------------------------------------------------------------------------------------------#
#####################################################################################################################################################
#---------------------------------------------------------------------------------------------------------------------------------------------------#
# Load essential packages:
import os, sys, ctypes
import pandas as pd
import numpy as np
from scipy.io import wavfile
#---------------------------------------------------------------------------------------------------------------------------------------------------#
#####################################################################################################################################################


'''
#####################################################################################################################################################
#---------------------------------------------------------------------------------------------------------------------------------------------------#
# Define the relative path to the API file:
rel_path_to_vtl = './PyVTL/API/VocalTractLabApi'
# Define the relative path to the speaker file:
rel_path_to_spk = './PyVTL/Speaker/'
# Load the VocalTractLab binary 'VocalTractLabApi.dll' if you use Windows or 'VocalTractLabApi.so' if you use Linux:
try:
	if sys.platform == 'win32':
		rel_path_to_vtl += '.dll'
	else:
		rel_path_to_vtl += '.so'
	VTL = ctypes.CDLL( rel_path_to_vtl )
except:
	print( 'Could not load the VocalTractLab API, does the path "{}" exist?'.format( rel_path_to_vtl ) )
#---------------------------------------------------------------------------------------------------------------------------------------------------#
#####################################################################################################################################################
'''


#####################################################################################################################################################
#---------------------------------------------------------------------------------------------------------------------------------------------------#
class vtl_params():
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	"""PyVTL Parameters""" 
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def __init__( self, *args ):
		self.state_samples  = 110     # Processrate in VTL (samples), currently 1 vocal tract state evaluation per 110 audio samples
		self.samplerate_audio = 44100 # Global audio samplerate (44100 Hz default)
		self.samplerate_internal = self.samplerate_audio / self.state_samples # Internal tract samplerate (ca. 400.9090... default)
		self.state_duration = 1 / self.samplerate_internal  # Processrate in VTL (time), currently 2.49433... ms
		self.verbose = True
		self.speaker_file_path = './PyVTL/Speaker/'
		self.speaker_file_name = self.speaker_file_path + 'JD2.speaker' # Default speaker file
#---------------------------------------------------------------------------------------------------------------------------------------------------#
#####################################################################################################################################################



#####################################################################################################################################################
#---------------------------------------------------------------------------------------------------------------------------------------------------#
class VTL():
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	"""A Python wrapper for VocalTractLab""" 
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def __init__( self, *args ):
		self.params = vtl_params( *args )
		self.API = self.load_API()
		self.get_version()
		self.initialize()
		return
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def __del__( self ):
		self.close()
		return
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def load_API( self ):
		rel_path_to_vtl = './PyVTL/API/VocalTractLabApi'
		# Load the VocalTractLab binary 'VocalTractLabApi.dll' if you use Windows or 'VocalTractLabApi.so' if you use Linux:
		try:
			if sys.platform == 'win32':
				rel_path_to_vtl += '.dll'
			else:
				rel_path_to_vtl += '.so'
			API = ctypes.CDLL( rel_path_to_vtl )
		except:
			print( 'Could not load the VocalTractLab API, does the path "{}" exist?'.format( rel_path_to_vtl ) )
		return API
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def initialize( self ):
		speaker_file_path = ctypes.c_char_p( self.params.speaker_file_name.encode() )
		failure = self.API.vtlInitialize( speaker_file_path )
		if failure != 0:
			raise ValueError('Error in vtlInitialize! Errorcode: %i' % failure)
		else:
			if self.params.verbose:
				print('VTL successfully initialized.')
		return
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def close( self ):
		self.API.vtlClose()
		if self.params.verbose:
			print('VTL successfully closed.')
		return
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def get_version( self ):
		#version = ctypes.c_char_p( b'                                ' )
		version = ctypes.c_char_p( ( ' ' * 32 ).encode() )
		self.API.vtlGetVersion( version )
		if self.params.verbose == True:
			print('Compile date of the library: "%s"' % version.value.decode() )
		return
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def get_constants( self ):
		audioSamplingRate = ctypes.c_int(0)
		numTubeSections = ctypes.c_int(0)
		numVocalTractParams = ctypes.c_int(0)
		numGlottisParams = ctypes.c_int(0)
		self.API.vtlGetConstants( ctypes.byref( audioSamplingRate ), 
			                      ctypes.byref( numTubeSections ),
			                      ctypes.byref( numVocalTractParams ),
			                      ctypes.byref( numGlottisParams ) 
			                     )
		constants = {
		'samplerate': audioSamplingRate.value,
		'n_tube_sections': numTubeSections.value,
		'n_tract_params': numVocalTractParams.value,
		'n_glottis_params': numGlottisParams.value,
		}
		#print(constants)
		return constants
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def get_param_info( self, params: str ):
		if params not in [ 'tract', 'glottis' ]:
			print( 'Unknown key in "get_param_info". Key must be "tract" or "glottis". Returning "tract" infos now.' )
			params = 'tract'
		if params == 'tract':
			key = 'n_tract_params'
		elif params == 'glottis':
			key = 'n_glottis_params'
		constants = self.get_constants()
		names = ctypes.c_char_p( ( ' ' * 10 * constants[ key ] ).encode() )
		paramMin        = ( ctypes.c_double * constants[ key ] )()
		paramMax        = ( ctypes.c_double * constants[ key ] )()
		paramNeutral    = ( ctypes.c_double * constants[ key ] )()
		if params == 'tract':
			self.API.vtlGetTractParamInfo( names, ctypes.byref( paramMin ), ctypes.byref( paramMax ), ctypes.byref( paramNeutral ) )
		elif params == 'glottis':
			self.API.vtlGetGlottisParamInfo( names, ctypes.byref( paramMin ), ctypes.byref( paramMax ), ctypes.byref( paramNeutral ) )
		df = pd.DataFrame( np.array( [ paramMin, paramMax, paramNeutral ] ).T, columns = [ 'min', 'max', 'neutral' ] )
		df.index = names.value.decode().strip( ' ' ).split( ' ' )
		print( df )
		return df
#---------------------------------------------------------------------------------------------------------------------------------------------------#
#	def get_tract_param_info( self ):
#		names, paramMin, paramMax, paramNeutral = get_param_info( key = 'tract' )
#		self.API.vtlGetTractParamInfo( ctypes.byref( names ), ctypes.byref( paramMin ), ctypes.byref( paramMax ), ctypes.byref( paramNeutral ) )
#		return
##---------------------------------------------------------------------------------------------------------------------------------------------------#
#	def get_glottis_param_info( self ):
#		names, paramMin, paramMax, paramNeutral = get_param_info( key = 'glottis' )
#		self.API.vtlGetGlottisParamInfo( ctypes.byref( names ), ctypes.byref( paramMin ), ctypes.byref( paramMax ), ctypes.byref( paramNeutral ) )
#		return
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def get_tract_params_from_shape( self, shape: str ): #Todo: glottis shapes as well
		shapeName = ctypes.c_char_p( shape.encode() )
		constants = self.get_constants()
		param = ( ctypes.c_double * constants[ 'n_tract_params' ] )()
		self.API.vtlGetTractParams( shapeName, ctypes.byref( param ) )
		#print( np.array( param ) )
		return np.array( param )
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def synth_block( self, tract_params, glottis_params, verbose = False, state_samples = None ):
		self.API.vtlSynthesisReset()
		constants = self.get_constants()
		if state_samples == None:
			state_samples = self.params.state_samples
		#tractParams = ctypes.c_double( tract_params )()
		#glottisParams = ctypes.c_double( tract_params )()
		if len( tract_params ) != len( glottis_params ):
			print( 'TODO: Warning: Length of tract_params and glottis_params do not match. Will modify glottis_params to match.')
			# Todo: Match length
		numFrames = ctypes.c_int( len( tract_params ) )
		#print( numFrames.value )
		tractParams = (ctypes.c_double * ( numFrames.value * constants[ 'n_tract_params' ] ))()
		glottisParams = (ctypes.c_double * ( numFrames.value * constants[ 'n_glottis_params' ] ))()
		tractParams[:] = tract_params.T.ravel('F')
		glottisParams[:] = glottis_params.T.ravel('F')
		#print( 'shape: {}'.format( np.array(tractParams).shape ) )
		#stop
		frameStep_samples = ctypes.c_int( state_samples )
		#print( frameStep_samples.value )
		audio = (ctypes.c_double * int( len( tract_params ) / self.params.samplerate_internal * self.params.samplerate_audio ) )()
		enableConsoleOutput = ctypes.c_int(1) if verbose == True else ctypes.c_int(0)
		return_val = self.API.vtlSynthBlock( tractParams, glottisParams, numFrames, frameStep_samples, audio, enableConsoleOutput )
		#print( return_val )
		return np.array( audio )
#---------------------------------------------------------------------------------------------------------------------------------------------------#
'''
	def export_tract_svg(double *tractParams, const char *fileName):
		return
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def tract_params_to_tube_data(double* tractParams,
  double* tubeLength_cm, double* tubeArea_cm2, int* tubeArticulator,
  double* incisorPos_cm, double* tongueTipSideElevation, double* velumOpening_cm2):
		return

#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def vtl_get_transfer_function(double *tractParams, int numSpectrumSamples,
  double *magnitude, double *phase_rad):
		return

#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def vtl_synthesis_reset():
		vtl.vtlSynthesisReset()
		return
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def vtlSynthesisAddTube(int numNewSamples, double *audio,
  double *tubeLength_cm, double *tubeArea_cm2, int *tubeArticulator,
  double incisorPos_cm, double velumOpening_cm2, double tongueTipSideElevation,
  double *newGlottisParams):
		return
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def vtlSynthesisAddTract(int numNewSamples, double *audio,
  double *tractParams, double *glottisParams):
		return

#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def synth_block( self, tract_params, glottis_params, verbose = False, state_samples = None ):
		constants = self.get_constants()
		if state_samples == None:
			state_samples = self.params.state_samples
		#tractParams = ctypes.c_double( tract_params )()
		#glottisParams = ctypes.c_double( tract_params )()
		if len( tract_params ) != len( glottis_params ):
			print( 'TODO: Warning: Length of tract_params and glottis_params do not match. Will modify glottis_params to match.')
			# Todo: Match length
		numFrames = ctypes.c_int( len( tract_params ) )
		tractParams = (ctypes.c_double * ( numFrames.value * constants[ 'n_tract_params' ] ))()
		glottisParams = (ctypes.c_double * ( numFrames.value * constants[ 'n_glottis_params' ] ))()
		tractParams[:] = tract_params.ravel('F')
		glottisParams[:] = glottis_params.ravel('F')
		frameStep_samples = ctypes.c_int( state_samples )
		audio = (ctypes.c_double * int( len( tract_params ) * self.params.samplerate_internal * self.params.samplerate_audio ) )()
		enableConsoleOutput = ctypes.c_int(1) if verbose == True else ctypes.c_int(0)
		self.API.vtlSynthBlock( tractParams, glottisParams, numFrames, frameStep_samples, audio, enableConsoleOutput )
		return np.array( audio )
#---------------------------------------------------------------------------------------------------------------------------------------------------#

vtlApiTest(const char *speakerFileName, double *audio, int *numSamples);
#---------------------------------------------------------------------------------------------------------------------------------------------------#

number_frames = int(duration * frame_rate)
		# Initialize VocalTractLab library
		audio = (ctypes.c_double * int(duration * VTL.Samplerate.value))()
		number_audio_samples = ctypes.c_int(0)

tract_params = (ctypes.c_double * (number_frames * VTL.N_VTP.value))()
		glottis_params = (ctypes.c_double * (number_frames * VTL.N_GP.value))()
		tube_areas = (ctypes.c_double * (number_frames * VTL.N_Tube_Sections.value))()
		tube_articulators = ctypes.c_char_p(b' ' * number_frames * VTL.N_Tube_Sections.value)
		# pass values to the C array
		#print(tract_params)
		tract_params[:] = tract_params_list.ravel('F')
		glottis_params[:] = glottis_params_list.ravel('F')

#---------------------------------------------------------------------------------------------------------------------------------------------------#
vtlTractSequenceToAudio(const char* tractSequenceFileName,
  const char* wavFileName, double* audio, int* numSamples);
#---------------------------------------------------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def segment_sequence_to_gestural_score( self, segFilePath, gesFilePath ):
		segFileName = ctypes.c_char_p( segFilePath.encode() )
		gesFileName = ctypes.c_char_p( gesFilePath.encode() )
		VTL.vtlSegmentSequenceToGesturalScore( segFileName, gesFileName )
		if self.params.verbose:
			print('Created gestural score from file: {}'.format( segFilePath ))
		return
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def gestural_score_to_tract_sequence( self, gesFilePath: str,  tractFilePath: str = '', return_Sequence: bool = False):
		gesFileName = ctypes.c_char_p( gesFilePath.encode() )
		if tractFilePath in (None, ''):
			tractFilePath = gesFilePath.split('.')[0] + '_tractSeq.txt'
		tractSequenceFileName = ctypes.c_char_p( tractFilePath.encode() )
		VTL.vtlGesturalScoreToTractSequence( gesFileName, tractSequenceFileName )
		if self.params.verbose:
			print('Created TractSeq of file: {}'.format( gesFilePath ))
		if return_Sequence:
			return self.tract_seq_to_df( tractFilePath )
		return
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def gestural_score_to_audio( self, ges_file_path: str,  audio_file_path: str = '' ):
		#wavFileName = ctypes.c_char_p(b'')
		wavFileName = ctypes.c_char_p( audio_file_path.encode() )
		gesFileName = ctypes.c_char_p( ges_file_path.encode() )
		audio = (ctypes.c_double * int( self.get_ges_score_length( ges_file_path ) * self.params.state_duration * self.params.samplerate_audio ))()
		numSamples = ctypes.c_int(0)
		VTL.vtlGesturalScoreToAudio( gesFileName, wavFileName, ctypes.byref(audio), ctypes.byref(numSamples) )
		if self.params.verbose:
			print( 'Audio generated from file: {}'.format( ges_file_path ) )
		#if audio_file_path != '':
		#	self.Write_Wav( self.Normalise_Wav(audio), audio_file_path )
		return np.array(audio)
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def tract_sequence_to_audio( self, TractSeq_Filename: str ):
		wavFileName = ctypes.c_char_p(b'')
		tractSequenceFileName = ctypes.c_char_p( TractSeq_Filename.encode() )
		audio = (ctypes.c_double * int( self.Get_Tract_Seq_Len(TractSeq_Filename) * self.params.state_duration * self.params.samplerate_audio ))()
		numSamples = ctypes.c_int(0)
		VTL.vtlTractSequenceToAudio( tractSequenceFileName, wavFileName, ctypes.byref(audio), ctypes.byref(numSamples) )
		if self.params.verbose:
			print('Audio generated: {}'.format(TractSeq_Filename))
		return np.array(audio)
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def get_gestural_score_duration( self, ges_file_path, return_samples ):
		return 2000
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def Get_Tract_Seq_Len( self, Input_Filename ):
		with open(Input_Filename) as file:
			for index, line in enumerate(file):
				if index == 7:
					TractSeq_Len = int(line.strip())
					break
		if self.params.verbose:
			print('Entries in Tract Sequence file: {}'.format(TractSeq_Len))
		return TractSeq_Len
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def tract_seq_to_df( self, tractFilePath ):
		# Skip rows from based on condition like skip every 3rd line
		df_GLP = pd.read_csv( tractFilePath, delim_whitespace = True, skiprows= lambda x: self.Read_Tract_Seq_GLP(x) , header = None )
		df_VTP = pd.read_csv( tractFilePath, delim_whitespace = True, skiprows= lambda x: self.Read_Tract_Seq_VTP(x) , header = None )
		if self.params.verbose:
			print('Tract Sequence opened: {}'.format( tractFilePath ))
		return df_GLP, df_VTP
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def Read_Tract_Seq_GLP(self, index):
		if (index > 7) and (index % 2 == 0):
			return False
		else:
			return True
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def Read_Tract_Seq_VTP(self, index):
		if (index > 7) and ((index-1) % 2 == 0):
			return False
		else:
			return True
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def df_to_tract_seq( self, outFilePath, df_GLP, df_VTP ):
		f= open( outFilePath, "w+" )
		f.write("""# The first two lines (below the comment lines) indicate the name of the vocal fold model and the number of states.\n""")
		f.write("""# The following lines contain the control parameters of the vocal folds and the vocal tract (states)\n""")
		f.write("""# in steps of 110 audio samples (corresponding to about 2.5 ms for the sampling rate of 44100 Hz).\n""")
		f.write("""# For every step, there is one line with the vocal fold parameters followed by\n""")
		f.write("""# one line with the vocal tract parameters.\n""")
		f.write("""# \n""")
		f.write("""Geometric glottis\n""")
		f.write("""{}\n""".format(len(df_GLP)))
		for index, row in enumerate(df_GLP.index):
			for index2, column in enumerate(df_GLP.columns):
				f.write('{} '.format(df_GLP.iloc[index,index2]))
			f.write('\n')
			for index2, column in enumerate(df_VTP.columns):
				f.write('{} '.format(df_VTP.iloc[index,index2]))
			f.write('\n')
		f.close()
		if self.params.verbose:
			print('Tract Sequence saved as: "{}"'.format( outFilePath ))
		return
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def Normalise_Wav(self, Input_Wav, normalisation = -1 ): #normalisation in dB
		norm_factor = 10**( -1 * normalisation * 0.05 ) -1
		#print(np.max(np.abs(Input_Wav),axis=0))
		norm_max = np.max(np.abs(Input_Wav),axis=0)
		Input_Wav /= ( norm_max + ( norm_max * norm_factor ) )
		print('Wav file normalised.')
		return Input_Wav
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def Write_Wav(self, Input_Wav, Output_Path, Samplerate = None ):
		if Samplerate == None:
			Samplerate = self.params.samplerate_audio
		wav_int = np.int16(Input_Wav * (2**15 - 1))
		wavfile.write(Output_Path, Samplerate, wav_int)
		print('Wav file saved.')
		return
#####################################################################################################################################################

'''