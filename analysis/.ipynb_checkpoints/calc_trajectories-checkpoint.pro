
;===================================================================================================

;                                                                                                  =

; calc_trajectories.pro                                                                            =

;                                                                                                  =

; Jonathan J. Rutz                                                                                 =

;                                                                                                  =

; written: May 10, 2013                                                                            =

; updated: Jun 29, 2013                                                                            =

;                                                                                                  =

;==================================================================================================;



pgmName = 'calc_trajectories.pro'



;==================================================================================================;

; Options                                                                                          ;

;==================================================================================================;



prt = 0

win = 5

topo = 0



pType       = 1   ; 1) plot trajectories   2) plot trajectory density



levList = [4,8,12,15,17,19,21] & nLevList = n_elements(levList)



Backward or forward trajectories

tDir = 1   ; 1) backward   2) forward



Number of hours for trajectories

nHourTraj = 72.

nRes      =  1.



;==================================================================================================;

; Definitions                                                                                      ;

;==================================================================================================;



const, miss



sYear = 1989 & eYear = 2010 & nYear = eYear - sYear + 1

nMon = 12 & monList = [0,1,2,3,10,11] & nMonList = n_elements(MonList)

nDay = 31

nHour = 24.

nXDay = 4



nTimeNorm = [31,28,31,30,31,30,31,31,30,31,30,31]*nXDay

nTimeLeap = [31,29,31,30,31,30,31,31,30,31,30,31]*nXDay



nStep = (nHourTraj/nRes)+1

timeRatio = ((nHour/nXDay)/nRes)



interpDir = '/uufs/chpc.utah.edu/common/home/steenburgh-group4/jon/traj/data/interp/'


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Domain over which trajectories will be calculated ;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; forward trajectories

if tDir eq 2 then begin

  sLon = 31 & eLon = 50 & nLon = eLon-sLon+1

  sLat = 25 & eLat = 44 & nlat = eLat-sLat+1

endif



; backward trajectories

if tDir eq 1 then begin

  sLon = 36 & eLon = 48 & nLon = eLon-sLon+1

  sLat = 21 & eLat = 38 & nlat = eLat-sLat+1

endif



;==================================================================================================;

; Data Acquisition                                                                                 ;


;==================================================================================================;



if fast eq 0 then begin



;--------------------------------------------------------------------------------------------------;

; ERA-Interim                                                                                      ;

;--------------------------------------------------------------------------------------------------;



iDir1 = '/uufs/chpc.utah.edu/common/home/steenburgh-group4/jon/era-interim/'

iDir2 = '/uufs/chpc.utah.edu/common/home/steenburgh-group4/jon/research/iwvt/data/old_plumes/'



; lon, lat, lev

;---------------



fileName = iDir1 + '4xDaily/hiResZ/u/hiResZ.u.201001.nc'

nc_open, filename, ID

vID = ncdf_varid(ID,'g0_lon_3')

ncdf_varget, ID, vID, lonEra

nLonEra = n_elements(lonEra)

vID = ncdf_varid(ID,'g0_lat_2')

ncdf_varget, ID, vID, latEra

nLatEra = n_elements(latEra)

vID = ncdf_varid(ID,'lv_ISBL1')

ncdf_varget, ID, vID, levEra

nLevEra = n_elements(levEra)

levEra *= 100.



minLon = -180.0 & maxLon =  180.0

minLat =    0.0 & maxLat =   90.0

junk = min(abs(lonEra - minLon), minLonInd) & junk = min(abs(lonEra - maxLon), maxLonInd)

junk = min(abs(latEra - minLat), minLatInd) & junk = min(abs(latEra - maxLat), maxLatInd)

if minLon lt 0.0 then nLonSel = maxLonInd - minLonInd + 1

if minLon gt 0.0 then nLonSel = nLonEra - (minLonInd - maxlonInd) + 1

nLatSel = minLatind - maxLatInd + 1 ; min/max switched in ERA-Interim

locStr = 'lon_' + strtrim(fix(minLon),2) + '-' + strtrim(fix(maxLon),2) + '_' $

       + 'lat_' + strtrim(fix(minLat),2) + '-' + strtrim(fix(maxLat),2)



;--------------------------------------------------------------------------------------------------;



fast = 1


endif



;==================================================================================================;

; Calculations                                                                                     ;

;==================================================================================================;



yearMon = '-99'

lastYearMon = '-99'


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Defining transects to search for ARs and then "launch" trajectories ;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;


; North American West Coast from 24 N to 52.5 N

;-----------------------------------------------

lonListWC = [31,33,34,36,36,36,36,36,36,36,37,38,39,40,41,42,43,43,44,45]

latListWC = [25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44]

nListWC = n_elements(lonListWC)



;; Interior Transect #1

;;----------------------

;lonListSC = [35,36,37,39,40,40,40,40,40,40,40,41,42,42,43,44,45,45,46,47] ;topo following

;latListSC = [23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42] ;topo following

;nListSC = n_elements(lonListSC)



;; Interior Transect #2

;;----------------------

lonListCD = [36,37,38,39,41,42,43,44,44,45,46,46,46,46,46,46,47,48] ; topo following

latListCD = [21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38] ; topo following

nListCD = n_elements(lonListCD)



;lonListAll = [lonListWC,lonListSC,lonListCD]

;latListAll = [latListWC,latListSC,latListCD]

lonListAll = [lonListCD]

latListAll = [latListCD]


nListAll = n_elements(lonListAll)



;**************************************************************************************************;

; Calculate Parcel Trajectories                                                                    ;

;**************************************************************************************************;



;--------------------------------------------------------------------------------------------------;

; Load data necessary to perform current trajectory                                                ;

;--------------------------------------------------------------------------------------------------;



;for iYear = 0, nYear-1 do begin

for iYear = 0, 0 do begin

  year = sYear + iYear

  if year/4 eq year/4. then leap = 1 else leap = 0

  if leap eq 1 then nTimeMon = nTimeLeap else nTimeMon = nTimeNorm

  for iMonList = 0, nMonList-1 do begin

;  for iMonList = 0, 0 do begin

    iMon = monList[iMonList]



;--------------------------------------------------------------------------------------------------;

; Create arrays to store monthly trajectory data                                                   ;


;--------------------------------------------------------------------------------------------------;


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; The arrays below were defined and calculated for each individual month ;;;
;;; and then stored, 124 is the number of potential 6-h time steps         ;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;


    lon_stats = fltarr(nLon,nLat,124,nLevList,  nStep)*miss ; parcel longitude

    lat_stats = fltarr(nLon,nLat,124,nLevList,  nStep)*miss ; parcel latitude

    lev_stats = fltarr(nLon,nLat,124,nLevList,  nStep)*miss ; parcel pressure level

    q_stats   = fltarr(nLon,nLat,124,nLevList,  nStep)*miss ; parcel specific humidity

    u_stats   = fltarr(nLon,nLat,124,nLevList,  nStep)*miss ; parcel u wind

    v_stats   = fltarr(nLon,nLat,124,nLevList,  nStep)*miss ; parcel v wind

    w_stats   = fltarr(nLon,nLat,124,nLevList,  nStep)*miss ; parcel w wind

    hw_stats  = fltarr(nLon,nLat,124,nLevList,  nStep)*miss ; parcel horizontal wind

    dr_stats  = fltarr(nLon,nLat,124,nLevList,  nStep)*miss ; parcel drying ratio (btwn last step and current)

    dq_stats  = fltarr(nLon,nLat,124,nLevList,  nStep)*miss ; change in q (btwn last step and current)

    ;ar_stats  = fltarr(nLon,nLat,124,nLevList,4,nStep)*miss ; is parcel location within an AR?

    ar_stats  = intarr(nLon,nLat,124,nLevList,4,nStep)*miss ; is parcel location within an AR?



    ; The 5th dimension of ar_stats is the parcel's yes/no "AR status":

    ; 0) is the parcel currently in an AR?

    ; 1) has the parcel been in an AR up to this point?

    ; 2) does the parcel make landfall in an AR?

    ; 3) if the parcel makes landfall in an AR, has it been in an AR up to this point




;--------------------------------------------------------------------------------------------------;



   ; handle dates - curr

    ;---------------------

    nTimeCurr = nTimeMon[iMon]

    strMon  = strtrim(iMon+1,2)

    if strMon le 9 then strMon = '0' + strMon

    strYear = strtrim(sYear+iYear,2)



    ; handle dates - next

    ;---------------------

    nextYear = iYear

    nextMon = iMon+1

    if iMon eq nMon-1 then begin

      nextYear = iYear+1 & nextMon = 0

    endif

    nTimeNext = nTimeMon[nextMon]

    strNextMon  = strtrim(nextMon+1,2)

    if strNextMon le 9 then strNextMon = '0' + strNextMon

    strNextYear = strtrim(sYear+nextYear,2)



    ; handle dates - prev

    ;---------------------

    prevYear = iYear

    prevMon = iMon-1

    if iMon eq 0 then begin

      prevYear = iYear-1 & prevMon = 11

    endif

    nTimePrev = nTimeMon[prevMon]

    strPrevMon  = strtrim(prevMon+1,2)

    if strPrevMon le 9 then strPrevMon = '0' + strPrevMon


    strPrevYear = strtrim(sYear+prevYear,2)