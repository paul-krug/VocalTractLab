#####################################################################################################################################################
#---------------------------------------------------------------------------------------------------------------------------------------------------#
#	- This file is a part of the VocalTractLab Python module PyVTL, see https://github.com/paul-krug/VocalTractLab
#---------------------------------------------------------------------------------------------------------------------------------------------------#
#
#	- Copyright (C) 2021, Paul Konstantin Krug, Dresden, Germany
#	- https://github.com/paul-krug/VocalTractLab
#	- Author: Paul Konstantin Krug, TU Dresden
#
#	- License info:
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

#---------------------------------------------------------------------------------------------------------------------------------------------------#
#####################################################################################################################################################
#---------------------------------------------------------------------------------------------------------------------------------------------------#
# Load essential packages:
import multiprocessing as mp
import tqdm
#---------------------------------------------------------------------------------------------------------------------------------------------------#
#####################################################################################################################################################


#---------------------------------------------------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------------------------------------------------#
def _run_multiprocessing( function, args, return_data, workers ):
	if workers == None:
		workers = mp.cpu_count()
	pool = mp.Pool( workers )
	tasks = ( ( function, x ) for x in args)
	data = None
	if return_data:
		data = []
		for x in tqdm.tqdm( pool.imap( _worker, tasks ), total=len( args ) ):
			data.append( x )
	else:
		for x in tqdm.tqdm( pool.imap( _worker, tasks ), total=len( args ) ):
			pass
	pool.close()
	pool.join()
	return data
#---------------------------------------------------------------------------------------------------------------------------------------------------#
def _worker( args ):
	function, arg = args
	return function( arg )
#---------------------------------------------------------------------------------------------------------------------------------------------------#
#####################################################################################################################################################