#!/usr/bin/env cmake -P
# vim:ft=cmake:

cmake_minimum_required(VERSION 3.3.1)

set(DATA_DIR data/)
set(TITLE "blosxom.cmake")

message("PATH_INFO = ${PATH_INFO}")
message("SCRIPT_NAME = $ENV{SCRIPT_NAME}")

# resolve symbolic link
get_filename_component(DATA_DIR ${DATA_DIR} REALPATH)
message("DATA_DIR = ${DATA_DIR}")

set(PATH_INFO "$ENV{PATH_INFO}")
if("${PATH_INFO}" STREQUAL "")
	set(PATH_INFO /2007/01/14)
endif()

string(REGEX MATCH "^/([0-9][0-9][0-9][0-9])(/([0-9][0-9])(/([0-9][0-9]))?)?" PATH_SEGS ${PATH_INFO})
set(PATH_YEAR ${CMAKE_MATCH_1})
set(PATH_MONTH ${CMAKE_MATCH_3})
set(PATH_DATE ${CMAKE_MATCH_5})
message("${PATH_SEGS} year=${PATH_YEAR} month=${PATH_MONTH} date=${PATH_DATE}")

string(REGEX MATCH "\\..+$" FLAVOUR ${PATH_INFO})
if("${FLAVOUR}" STREQUAL "")
	set(FLAVOUR "html")
endif()
message("FLAVOUR = ${FLAVOUR}")

string(REGEX REPLACE "(index)?\\..+$" "" PATH_INFO ${PATH_INFO})

# get .txt files
file(GLOB_RECURSE files LIST_DIRECTORIES false ${DATA_DIR}/*.txt)

# sort by mtime
set(sorted)
foreach(file IN LISTS files)
	file(TIMESTAMP "${file}" mtime)
	file(RELATIVE_PATH rel ${DATA_DIR} ${file})
	# construct list as 2007-02-07T03:08:40:/path/to/entry.txt
	list(APPEND sorted "${mtime}:${file}")
endforeach()
list(SORT sorted)
list(REVERSE sorted)
set(files)
foreach(item IN LISTS sorted)
	string(LENGTH ${item} len)
	string(SUBSTRING ${item} 20 ${len} file)
	list(APPEND files ${file})
endforeach()


# filter by PATH_INFO
set(filtered)
if("${PATH_YEAR}" STREQUAL "")
	# filter by path name
	foreach(file IN LISTS files)
		file(RELATIVE_PATH rel ${DATA_DIR} ${file})
		string(REGEX MATCH "^${PATH_INFO}" match /${rel})
		if(NOT "${match}" STREQUAL "")
			list(APPEND filtered ${file})
		endif()
	endforeach()
else()
	if("${PATH_MONTH}" STREQUAL "")
		# filter by year
		foreach(file IN LISTS files)
			file(TIMESTAMP "${file}" year "%Y")
			if("${year}" STREQUAL "${PATH_YEAR}")
				list(APPEND filtered ${file})
			endif()
		endforeach()
	else()
		if("${PATH_DATE}" STREQUAL "")
			# filter by year and month
			foreach(file IN LISTS files)
				file(TIMESTAMP "${file}" yearmonth "%Y-%m")
				if("${yearmonth}" STREQUAL "${PATH_YEAR}-${PATH_MONTH}")
					list(APPEND filtered ${file})
				endif()
			endforeach()
		else()
			# filter by year, month and date
			foreach(file IN LISTS files)
				file(TIMESTAMP "${file}" yearmonthdate "%Y-%m-%d")
				if("${yearmonthdate}" STREQUAL "${PATH_YEAR}-${PATH_MONTH}-${PATH_DATE}")
					list(APPEND filtered ${file})
				endif()
			endforeach()
		endif()
	endif()
endif()
set(files ${filtered})

# XXX
# message() output to stderr
# message(STATUS ...) prepend "--" to message
# so write stdout directly...
function(echo string)
	file(WRITE /dev/stdout ${string})
endfunction()

# output entries
file(READ "head.${FLAVOUR}" content)
string(REPLACE "#{home}" "$ENV{SCRIPT_NAME}" content ${content})
string(REPLACE "#{title}" "${TITLE}" content ${content})
echo(${content})

foreach(file IN LISTS files)
	file(RELATIVE_PATH name ${DATA_DIR} ${file})
	string(REGEX REPLACE "\\..+$" "" name ${name})
	file(TIMESTAMP ${file} date "%Y-%m-%d %H:%M:%S")

	file(READ ${file} body)
	string(LENGTH "${body}" len)
	string(FIND "${body}\n" "\n" pos)
	string(SUBSTRING "${body}" 0 ${pos} title)
	string(SUBSTRING "${body}" ${pos} ${len} body)

	file(READ "story.${FLAVOUR}" content)
	string(REPLACE "#{home}" "$ENV{SCRIPT_NAME}" content ${content})
	string(REPLACE "#{name}" "${name}" content ${content})
	string(REPLACE "#{date}" "${date}" content ${content})
	string(REPLACE "#{title}" "${title}" content ${content})
	string(REPLACE "#{body}" "${body}" content ${content})
	echo(${content})
endforeach()

file(READ "foot.${FLAVOUR}" content)
string(REPLACE "#{version}" "${CMAKE_VERSION}" content ${content})
echo(${content})

