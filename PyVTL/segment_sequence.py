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
#__version__ = '0.1'
#__author__ = 'Paul Konstantin Krug'
#---------------------------------------------------------------------------------------------------------------------------------------------------#
#####################################################################################################################################################
#---------------------------------------------------------------------------------------------------------------------------------------------------#
# Load essential packages:
import os
import warnings
import pandas as pd
import numpy as np
import PyVTL.VocalTractLabApi as vtl
import PyVTL.function_tools as FT
import matplotlib.pyplot as plt
from  itertools import chain
import math
#---------------------------------------------------------------------------------------------------------------------------------------------------#
#####################################################################################################################################################


#####################################################################################################################################################
#---------------------------------------------------------------------------------------------------------------------------------------------------#
class Segment_Sequence():
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	"""PyVTL segment sequences""" 
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def __init__( self, phonemes: list, durations: list, onset_duration: float, offset_duration: float = 0.0 ):
		self.durations = FT.check_if_list_is_valid( durations, (int, float) )
		self.phonemes = FT.check_if_list_is_valid( phonemes, (str) )
		self.onset_duration = onset_duration
		self.offset_duration = offset_duration
		self.effects = [ None for _ in self.phonemes ]

		#self.data = pd.DataFrame( columns = [ 'onset', 'offset', 'duration', 'index', 'phoneme', 'effect', 'degenerated' ] )
		return
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	@classmethod
	def from_audio_file( cls, audio_file_path, phonemes = None, text = None, optimize = False, language = 'de' ): #'TODO'
		if phonemes == None:
			if text == None:
				text = ASR( audio_file_path )
			phonemes = G2P.text_to_sampa( text, language )
		boundaries = Boundaries.uniform_from_audio_file( audio_file_path = audio_file_path, n_phonemes = len( phonemes ) )
		return cls( phonemes, boundaries )
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	@classmethod
	def from_seg_file( self, seg_file_path ): #'TODO'
		phonemes = []
		durations = []
		boundary_times = []
		with open( seg_file_path ) as file:
			for line in file:
				if len(line.strip()) != 0 :
					items = line.strip().split(';')
					for item in [x for x in items if x]:
						label = item.split('=')[0].strip()
						value = item.split('=')[1].strip()
						#print('Label: {}'.format(label))
						#print('Value: {}'.format(value))
						if label =='name' and (value not in [None," ", ""]):
							phonemes.append( value )
						if label == 'duration_s':
							durations.append( float( value ) )
		return cls( phonemes, boundaries )
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def __del__( self ):
		#print( 'Segment sequence destroyed.' )
		return
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def __str__( self ):
		boundaries = [ self.onset_duration ]
		for index, duration in enumerate( self.durations ):
			boundaries.append( boundaries[-1] + duration )
		data = [ boundaries[ :-1 ], boundaries[ 1: ], self.durations, self.phonemes, self.effects ]
		return str( pd.DataFrame( data, columns=[ 'onset', 'offset', 'duration', 'phoneme', 'effect'] ) )
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def _get_phoneme_boundary_times( self, file_path: str, n_phonemes: int ):
		data, samplerate = librosa.load( file_path, 44100 )
		onset, offset = detect_onset_and_offset( file_path )
		duration = len( data )
		start = onset
		end =  offset
		print( 'num phon: {}'.format(n_phonemes) )
		print( 'onset: {}'.format( onset ) )
		print( 'offset: {}'.format( offset ) )
		preds = [ x for x in np.arange( start, end, (end-start)/(n_phonemes) ) ] #+1*round( (end-start)/number_phonemes)
		preds.append( offset )
		print( 'returning {} boundaries'.format(len(preds)) )
		return preds
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def _get_uniform_durations_from_audio_file( self, ):
		return
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def assimilation( self, language = 'de' ): # Assimilation rules for German 
		phonemes = self._phonemes
		for index, phone in enumerate( phonemes ):
			if index >= 2 and phone.name == 'n' and ( phonemes[ index - 1 ].name in ['p','b'] or ( phonemes[ index - 1 ].name == '@' and phonemes[ index - 2 ].name in ['p','b'] ) ):
				self.effect[ index ] = 'm'
			if index >= 2 and phone.name == 'n' and ( phonemes[ index - 1 ].name in ['g','k'] or ( phonemes[ index - 1 ].name == '@' and phonemes[ index - 2 ].name in ['g','k'] ) ):
				self.effect[ index ] = 'N'
		return
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def elision( self, language = 'de' ): # Elision rules for German
		phonemes = self._phonemes
		for index, phone in enumerate( phonemes ):
			if phone.name == '@' and phonemes[ index + 1 ].is_sonorant():
				self.effect[ index ] = 'elision'
		return
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def export_seg( self, file_path, account_for_effects = False ):
		assert len( self._phonemes ) == len( self._boundaries.times ) - 1, 'Lengths do not match'
		out_file = open( file_path, 'w+' )
		out_file.write( 'name = {}; duration_s = {};\n'.format( '', self.silence_onset ) )
		for index, phoneme in enumerate( self._phonemes ):
			if account_for_effects == False or ( account_for_effects == True and self.effect[ index ] != 'elision' ):
				if self.effect[ index ] != None and self.effect[ index ] != 'elision':
					output_phone = self.effect[ index ]
				else:
					output_phone = phoneme.name
				out_file.write( 'name = {}; duration_s = {};\n'.format( output_phone, self._boundaries.intervals[ index ] ) )
		out_file.write( 'name = {}; duration_s = {};\n'.format( '', self.silence_offset ) )
		return
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def get_variants( self, account_for_effects = 'on' ):
		assert len( self._phonemes ) == len( self._boundaries.times ) - 1, 'Lengths do not match'

		phonemes = []
		#boundary_times = []
		for index, phoneme in enumerate( self._phonemes ):
			if self.effect[ index ] != 'elision':
				if self.effect[ index ] != None and self.effect[ index ] != 'elision':
					phonemes.append( self.effect[ index ] )
				else:
					phonemes.append( phoneme.name )
			start = self._boundaries.times[ 0 ]
			end = self._boundaries.times[ -1 ]
			boundary_times = [ x for x in np.arange( start, end, (end-start)/( len(phonemes) ) ) ]
			boundary_times.append( end )

		return [ self, Segment_Sequence( phonemes, Boundaries( boundary_times ) ) ]
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def import_seg( self, file_path ):
		return
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def get_phoneme_names( self, ):
		return [ phoneme.name for phoneme in self._phonemes ]
#---------------------------------------------------------------------------------------------------------------------------------------------------#
#####################################################################################################################################################


#####################################################################################################################################################
class Segment_Sequence2():
	def __init__( self, boundaries: list, sampa: list, name: str = 'sequence.seg' ):
		boundaries = FT.check_if_list_is_valid( boundaries, (int, float) )
		sampa = FT.check_if_list_is_valid( sampa, (str) )


		self.param_info = { 'tract': tract_states.param_info, 'glottis': glottis_states.param_info }
		self.name = name
		self.tract = tract_states.tract
		self.glottis = glottis_states.glottis
		lengths_difference = np.abs( tract_states.length - glottis_states.length )
		if tract_states.length > glottis_states.length:
			warnings.warn( 'lengths of supra glottal sequence is longer than sub glottal sequence. Will pad the sub glottal sequence now.' )
			self.glottis = pd.concat( 
			                             [ self.glottis, 
										   pd.DataFrame( [ self.glottis.iloc[ -1, : ] for _ in range(0, lengths_difference ) ] )
										 ], 
										 ignore_index = True 
										 )
		elif tract_states.length < glottis_states.length:
			warnings.warn( 'lengths of supra glottal sequence is shorter than sub glottal sequence. Will pad the supra glottal sequence now.' )
			self.tract = pd.concat( 
			                             [ self.tract, 
										   pd.DataFrame( [ self.tract.iloc[ -1, : ] for _ in range(0, lengths_difference ) ] )
										 ], 
										 ignore_index = True 
										 )
		if len( self.tract.index ) != len( self.glottis.index ):
			print( 'ultra fail' )
		self.length = len( self.tract.index )
		return
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def __str__( self, ):
		return str( pd.concat( [ self.tract, self.glottis ], axis = 1 ) )
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	@classmethod
	def from_tract_file( cls, tract_file_path ):
		df_GLP = pd.read_csv( tract_file_path, delim_whitespace = True, skiprows= lambda x: read_tract_seq_GLP(x) , header = None )
		df_VTP = pd.read_csv( tract_file_path, delim_whitespace = True, skiprows= lambda x: read_tract_seq_VTP(x) , header = None )
		return cls( Supra_Glottal_Sequence( df_VTP.to_numpy() ), Sub_Glottal_Sequence( df_GLP.to_numpy() ), tract_file_path )
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def apply_biomechanical_constraints( self, ):
		self.tract = vtl.tract_sequence_to_limited_tract_sequence( self.tract ).tract
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def insert( self, parameter, trajectory, trajectory_sr = None, start = 0, time_axis = 'samples', padding = None, smooth = True ):
		if parameter in self.tract.columns:
			feature = self.tract
		elif parameter in self.glottis.columns:
			feature = self.glottis
		else:
			#if parameter not in chain( *[ self.tract.columns, self.glottis.columns ] ):
			raise ValueError( 'The specified parameter: {} is neither a supra glottal nor a sub glottal parameter!'.format( parameter ) )
		if time_axis not in [ 'seconds', 'samples' ]:
			raise ValueError( 'Argument "time_axis" must be "seconds" or "samples", not "{}"!'.format( time_axis ) )
		trajectory = FT.check_if_list_is_valid( trajectory, (int, float) )
		state_sr = 44100/110
		if trajectory_sr != None:
			trajectory = resample_trajectory( trajectory, trajectory_sr, state_sr )
		if time_axis == 'seconds':
			start = round( state_sr * start )
		if padding == 'same':
			trajectory = [ trajectory[0] for _ in range(0, start) ] + trajectory + [ trajectory[-1] for _ in range( start + len( trajectory ), len(feature[parameter]) ) ] 
			#plt.plot(trajectory)
			#plt.show()
			feature[ parameter ] = trajectory
		else:	
			feature.loc[ start : start + len( trajectory ) - 1, parameter ] = trajectory
		#values_a = feature.loc[ : start, parameter ].to_list()
		#values_b = feature.loc[ : start, parameter ].to_list()
		#smooth_values_1 = transition( values_a, resampled_values, 40, fade='in' )
		#smooth_values_2 = transition( smooth_values_1, values_b, 40, fade='out' )
		#print(len(smooth_values_2))
		#feature.loc[ 0 : len( smooth_values_2 )-1, parameter ] = smooth_values_2
		return
#---------------------------------------------------------------------------------------------------------------------------------------------------#
	def plot( self, parameters = ['LP','JA','LD','HX','HY'], n_params = 19 ):
		figure, axs = plt.subplots( len(parameters), figsize = (8, 4/3 *len(parameters) ), sharex = True, gridspec_kw = {'hspace': 0} )
		#figure.suptitle( 'Sharing both axes' )
		#parameters = self.tract.columns
		for index, parameter in enumerate( parameters ):
			axs[ index ].plot( self.tract.loc[ :, parameter ] )
			axs[ index ].set( ylabel = parameter )
		plt.xlabel( 'Tract state' )
		for ax in axs:
		    ax.label_outer()
		figure.align_ylabels( axs[:] )
		plt.show()
		return
#####################################################################################################################################################



#---------------------------------------------------------------------------------------------------------------------------------------------------#
def read_tract_seq_GLP( index ):
	if (index > 7) and (index % 2 == 0):
		return False
	else:
		return True
#---------------------------------------------------------------------------------------------------------------------------------------------------#
def read_tract_seq_VTP( index ):
	if (index > 7) and ((index-1) % 2 == 0):
		return False
	else:
		return True
#---------------------------------------------------------------------------------------------------------------------------------------------------#