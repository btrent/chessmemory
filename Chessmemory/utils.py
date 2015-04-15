def get_version():
    return "0.2"
    
def get_license():
    return """Chessmemory is free software; you can redistribute it and/or modify 
it under the terms of the GNU General Public License as published by 
the Free Software Foundation; either version 2 of the License, or 
(at your option) any later version.

Chessmemory is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
GNU General Public License for more details.

You should have received a copy of the GNU General Public License 
along with Chessmemory; if not, write to the Free Software Foundation, Inc., 
51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA"""

def locate_data_dir():
    # FIXME: add logic
    #return "/usr/local/share/chessmemory/"
    return "data/"
    
def nag_replace(nag):
    if nag == "$0": return ""
    elif nag == "$1": return "!"
    elif nag == "$2": return "?"
    elif nag == "$3": return "!!"
    elif nag == "$4": return "??"
    elif nag == "$5": return "!?"
    elif nag == "$6": return "?!"
    elif nag == "$11": return "="
    elif nag == "$14": return "+="
    elif nag == "$15": return "=+"
    elif nag == "$16": return "+/-"
    elif nag == "$17": return "-/+"
    elif nag == "$18": return "+-"
    elif nag == "$19": return "-+"
    elif nag == "$20": return "+--"
    elif nag == "$21": return "--+"
    else: return nag
    
