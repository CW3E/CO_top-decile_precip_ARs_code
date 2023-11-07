
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


; ?? Are this the indices of the vertical levels? ;

levList = [4,8,12,15,17,19,21] & nLevList = n_elements(levList)


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Backward or forward trajectories ;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

tDir = 1   ; 1) backward   2) forward


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Number of hours for trajectories ;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

nHourTraj = 72.

nRes      =  1. ; ?? Is this the temporal resoltion?



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



    for iTime = 0, nTimeMon[iMon]-1 do begin

      print, iYear, iMon, iTime

      skip = 0



      ; handle currently non-calculable dates - prev

      ;----------------------------------------------

      if tDir eq 1 then begin

        if iYear eq 0 and iMon eq 0 and iTime lt ((nStep-1)/(nHour/nXDay)) then skip = 1

        if iMon eq 10 and iTime lt ((nStep-1)/(nHour/nXDay)) then skip = 1

      endif



      ; handle currently non-calculable dates - next

      ;----------------------------------------------

      if tDir eq 2 then begin

        if iYear eq nYear-1 and iMon eq nMon-1 and iTime gt 124-((nStep-1)/(nHour/nXDay)) then skip = 1

        if iMon eq 3 and iTime gt 120-((nStep-1)/(nHour/nXDay)) then skip = 1

      endif



      if skip eq 0 then begin


        yearmon = strYear + strMon



;**************************************************************************************************;

; Backward trajectories                                                                            ;

;**************************************************************************************************;



Here I am loading previously interpolated ERA-Interim data (from 6-h to 1-h) and putting it into arrays



        if tDir eq 1 then begin

          if yearmon ne lastYearmon then begin

            u = fltarr(nLonSel,nLatSel,nLevEra,6*(nTimePrev+nTimeCurr))

            v = fltarr(nLonSel,nLatSel,nLevEra,6*(nTimePrev+nTimeCurr))

            w = fltarr(nLonSel,nLatSel,nLevEra,6*(nTimePrev+nTimeCurr))

            q = fltarr(nLonSel,nLatSel,nLevEra,6*(nTimePrev+nTimeCurr))

            a = intarr(nLonSel,nLatSel,        6*(nTimePrev+nTimeCurr))

            print, 'loading new data...'



            ; load interpolated data from month in which trajectory is initiated

            ;--------------------------------------------------------------------

            restore, interpDir + 'q_interp_' + locStr + '_' + strYear + '_' + strMon + '.sav'

            restore, interpDir + 'u_interp_' + locStr + '_' + strYear + '_' + strMon + '.sav'

            restore, interpDir + 'v_interp_' + locStr + '_' + strYear + '_' + strMon + '.sav'

            restore, interpDir + 'w_interp_' + locStr + '_' + strYear + '_' + strMon + '.sav'

            restore, interpDir + 'plumes_interp_' + locStr + '_' + strYear + '_' + strMon + '.sav'

            q[*,*,*,6*nTimePrev:6*nTimePrev+6*nTimeCurr-1] = q_interp[*,*,*,*]

            u[*,*,*,6*nTimePrev:6*nTimePrev+6*nTimeCurr-1] = u_interp[*,*,*,*]

            v[*,*,*,6*nTimePrev:6*nTimePrev+6*nTimeCurr-1] = v_interp[*,*,*,*]

            w[*,*,*,6*nTimePrev:6*nTimePrev+6*nTimeCurr-1] = w_interp[*,*,*,*]

            a[*,*,  6*nTimePrev:6*nTimePrev+6*nTimeCurr-1] = plumes_interp[*,*,*,*]



            ; load data from month prior to that in which trajectory is initiated

            ;---------------------------------------------------------------------

            if iMon ne 10 then begin

              skip2 = 0

              if iYear eq 0 and iMon eq 0 then skip2 = 1

              if skip2 eq 0 then begin

                restore, interpDir + 'q_interp_' + locStr + '_' + strPrevYear + '_' + strPrevMon + '.sav'

                restore, interpDir + 'u_interp_' + locStr + '_' + strPrevYear + '_' + strPrevMon + '.sav'

                restore, interpDir + 'v_interp_' + locStr + '_' + strPrevYear + '_' + strPrevMon + '.sav'

                restore, interpDir + 'w_interp_' + locStr + '_' + strPrevYear + '_' + strPrevMon + '.sav'

                restore, interpDir + 'plumes_interp_' + locStr + '_' + strPrevYear + '_' + strPrevMon + '.sav'

                q[*,*,*,0:6*nTimePrev-1] = q_interp[*,*,*,*]

                u[*,*,*,0:6*nTimePrev-1] = u_interp[*,*,*,*]

                v[*,*,*,0:6*nTimePrev-1] = v_interp[*,*,*,*]

                w[*,*,*,0:6*nTimePrev-1] = w_interp[*,*,*,*]

                a[*,*,  0:6*nTimePrev-1] = plumes_interp[*,*,*]

              endif ; skip eq 0

            endif ; iMon ne 10

          endif ; yearmon


        endif ; tDir eq 1



;**************************************************************************************************;

; Forward trajectories                                                                             ;

;**************************************************************************************************;



        if tDir eq 2 then begin

          if yearmon ne lastYearmon then begin

            u = fltarr(nLonSel,nLatSel,nLevEra,6*(nTimeCurr+nTimeNext))*miss

            v = fltarr(nLonSel,nLatSel,nLevEra,6*(nTimeCurr+nTimeNext))*miss

            w = fltarr(nLonSel,nLatSel,nLevEra,6*(nTimeCurr+nTimeNext))*miss

            q = fltarr(nLonSel,nLatSel,nLevEra,6*(nTimeCurr+nTimeNext))*miss

            a = intarr(nLonSel,nLatSel,        6*(nTimeCurr+nTimeNext))*miss

            print, 'loading new data...'



            ; load interpolated data from month in which trajectory is initiated

            ;--------------------------------------------------------------------

            restore, interpDir + 'q_interp_' + locStr + '_' + strYear + '_' + strMon + '.sav'

            restore, interpDir + 'u_interp_' + locStr + '_' + strYear + '_' + strMon + '.sav'

            restore, interpDir + 'v_interp_' + locStr + '_' + strYear + '_' + strMon + '.sav'

            restore, interpDir + 'w_interp_' + locStr + '_' + strYear + '_' + strMon + '.sav'

            restore, interpDir + 'plumes_interp_' + locStr + '_' + strYear + '_' + strMon + '.sav'

            q[*,*,*,0:6*nTimeCurr-1] = q_interp[*,*,*,*]

            u[*,*,*,0:6*nTimeCurr-1] = u_interp[*,*,*,*]

            v[*,*,*,0:6*nTimeCurr-1] = v_interp[*,*,*,*]

            w[*,*,*,0:6*nTimeCurr-1] = w_interp[*,*,*,*]

            a[*,*,  0:6*nTimeCurr-1] = plumes_interp[*,*,*,*]



            ; load data from month after that in which trajectory is initiated

            ;------------------------------------------------------------------

            if iMon ne 3 then begin

              skip2 = 0

              if iYear eq nYear-1 and iMon eq nMon-1 then skip2 = 1

              if skip2 eq 0 then begin

                restore, interpDir + 'q_interp_' + locStr + '_' + strNextYear + '_' + strNextMon + '.sav'

                restore, interpDir + 'u_interp_' + locStr + '_' + strNextYear + '_' + strNextMon + '.sav'

                restore, interpDir + 'v_interp_' + locStr + '_' + strNextYear + '_' + strNextMon + '.sav'

                restore, interpDir + 'w_interp_' + locStr + '_' + strNextYear + '_' + strNextMon + '.sav'

                restore, interpDir + 'plumes_interp_' + locStr + '_' + strNextYear + '_' + strNextMon + '.sav'

                q[*,*,*,6*nTimeCurr:6*nTimeCurr+6*nTimeNext-1] = q_interp[*,*,*,*]

                u[*,*,*,6*nTimeCurr:6*nTimeCurr+6*nTimeNext-1] = u_interp[*,*,*,*]

                v[*,*,*,6*nTimeCurr:6*nTimeCurr+6*nTimeNext-1] = v_interp[*,*,*,*]

                w[*,*,*,6*nTimeCurr:6*nTimeCurr+6*nTimeNext-1] = w_interp[*,*,*,*]

                a[*,*,  6*nTimeCurr:6*nTimeCurr+6*nTimeNext-1] = plumes_interp[*,*,*]

              endif ; skip eq 0

            endif ; iMon ne 3

          endif ; yearmon


        endif ; tDir eq 2



;--------------------------------------------------------------------------------------------------;

; Loop over all lats/lons                                                                          ;

;--------------------------------------------------------------------------------------------------;



for iLon = sLon, eLon do begin

  for iLat = sLat, eLat do begin



;************************************

for iList = 0, nListAll-1 do begin

  if iLon eq lonListAll[iList] and iLat eq latListAll[iList] then begin

;************************************



    for iLevList = 0, nLevList-1 do begin

      iLev = levList[iLevList]

      if tDir eq 1 then jTime = 6*nTimePrev+6*iTime

      if tDir eq 2 then jTime =             6*iTime



      arStreak   = 0

      arStreakLF = 0

      LF_check = 0

      for iStep = 0, nStep-1 do begin



qgrid0 = reform(q[*,*,*,jTime])

ugrid0 = reform(u[*,*,*,jTime])

vgrid0 = reform(v[*,*,*,jTime])

wgrid0 = reform(w[*,*,*,jTime])



if iStep eq 0 then begin

  lon_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep] = lonEra[iLon]

  lat_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep] = latEra[iLat]

  lev_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep] = levEra[iLev]

  q_stats  [iLon-sLon,iLat-sLat,iTime,iLevList,iStep] = qgrid0[iLon,iLat,iLev]

  u_stats  [iLon-sLon,iLat-sLat,iTime,iLevList,iStep] = ugrid0[iLon,iLat,iLev]

  v_stats  [iLon-sLon,iLat-sLat,iTime,iLevList,iStep] = vgrid0[iLon,iLat,iLev]

  w_stats  [iLon-sLon,iLat-sLat,iTime,iLevList,iStep] = wgrid0[iLon,iLat,iLev]

  hw_stats [iLon-sLon,iLat-sLat,iTime,iLevList,iStep] = sqrt((ugrid0[iLon,iLat,iLev]^2)+(vgrid0[iLon,iLat,iLev]^2))

endif else begin

  if lon_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep] lt -180 then $

      lon_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep] += 360.

  lonbin = value_locate(lonEra,lon_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep])

  lon0 = lonbin & lon1 = lonbin+1

  if lon1 ge 240 then lon1 -=240.

  latbin = value_locate(latEra,lat_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep])

  lat0 = latbin & lat1 = latbin+1

  levbin = value_locate(levEra,lev_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep])

  lev0 = levbin & lev1 = levbin+1


  if lev1 gt 23 then lev1 = 23 & check = 1



if lat0 le 0 then break ; don't cross the north pole

if lat1 le 0 then break ; don't cross the north pole

if lat0 ge 61 then break ; don't cross the equator

if lat1 ge 61 then break ; don't cross the equator



Below I am basically finding where the parcel is located relative to surrounding grid points



; calculate fractional distance between parcel position (x,y,z) and nearest grid points (x,y,z) in

; both directions

;-------------------------------------------------------------------------------------------------

lonD = (lon_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep]-lonEra[lon0])/(lonEra[lon1]-lonEra[lon0])

latD = (lat_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep]-latEra[lat0])/(latEra[lat1]-latEra[lat0])

levD = (lev_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep]-levEra[lev0])/(levEra[lev1]-levEra[lev0])


if check eq 1 then levD = 0



; perform interpolation along lon (x)

;------------------------------------

q00 = qgrid0[lon0,lat0,lev0]*(1-lonD)+qgrid0[lon1,lat0,lev0]*lonD

q10 = qgrid0[lon0,lat1,lev0]*(1-lonD)+qgrid0[lon1,lat1,lev0]*lonD

q01 = qgrid0[lon0,lat0,lev1]*(1-lonD)+qgrid0[lon1,lat0,lev1]*lonD

q11 = qgrid0[lon0,lat1,lev1]*(1-lonD)+qgrid0[lon1,lat1,lev1]*lonD

u00 = ugrid0[lon0,lat0,lev0]*(1-lonD)+ugrid0[lon1,lat0,lev0]*lonD

u10 = ugrid0[lon0,lat1,lev0]*(1-lonD)+ugrid0[lon1,lat1,lev0]*lonD

u01 = ugrid0[lon0,lat0,lev1]*(1-lonD)+ugrid0[lon1,lat0,lev1]*lonD

u11 = ugrid0[lon0,lat1,lev1]*(1-lonD)+ugrid0[lon1,lat1,lev1]*lonD

v00 = vgrid0[lon0,lat0,lev0]*(1-lonD)+vgrid0[lon1,lat0,lev0]*lonD

v10 = vgrid0[lon0,lat1,lev0]*(1-lonD)+vgrid0[lon1,lat1,lev0]*lonD

v01 = vgrid0[lon0,lat0,lev1]*(1-lonD)+vgrid0[lon1,lat0,lev1]*lonD

v11 = vgrid0[lon0,lat1,lev1]*(1-lonD)+vgrid0[lon1,lat1,lev1]*lonD

w00 = wgrid0[lon0,lat0,lev0]*(1-lonD)+wgrid0[lon1,lat0,lev0]*lonD

w10 = wgrid0[lon0,lat1,lev0]*(1-lonD)+wgrid0[lon1,lat1,lev0]*lonD

w01 = wgrid0[lon0,lat0,lev1]*(1-lonD)+wgrid0[lon1,lat0,lev1]*lonD

w11 = wgrid0[lon0,lat1,lev1]*(1-lonD)+wgrid0[lon1,lat1,lev1]*lonD



; perform interpolation along lat (y)

;------------------------------------

q0 = q00*(1-latD)+q10*latD & q1 = q01*(1-latD)+q11*latD

u0 = u00*(1-latD)+u10*latD & u1 = u01*(1-latD)+u11*latD

v0 = v00*(1-latD)+v10*latD & v1 = v01*(1-latD)+v11*latD

w0 = w00*(1-latD)+w10*latD & w1 = w01*(1-latD)+w11*latD



; perform interpolation along lev (z)

;------------------------------------

q_stats [iLon-sLon,iLat-sLat,iTime,iLevList,iStep] = q0*(1-levD)+q1*levD

u_stats [iLon-sLon,iLat-sLat,iTime,iLevList,iStep] = u0*(1-levD)+u1*levD

v_stats [iLon-sLon,iLat-sLat,iTime,iLevList,iStep] = v0*(1-levD)+v1*levD

w_stats [iLon-sLon,iLat-sLat,iTime,iLevList,iStep] = w0*(1-levD)+w1*levD

hw_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep] = $

    sqrt((u_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep]^2)+(v_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep]^2))



endelse



; determine the parcel's "AR status"

;-----------------------------------

junk = min(abs(lonEra - lon_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep]), closestLon)

junk = min(abs(latEra - lat_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep]), closestLat)



if a[closestLon,closestLat,jTime] eq 1 then begin


  ar_stats[iLon-sLon,iLat-sLat,iTime,iLevList,0,iStep] = 1



  ; determine if parcel makes landfall within AR

  ;----------------------------------------------

  if LF_check eq 0 then begin

    ;for iListWC = 0, nCoast-1 do begin

    for iListWC = 0, nListWC-1 do begin

      ;if closestLon eq lonCoast[iCoast] and closestLat eq latCoast[iCoast] then begin

      if closestLon eq lonListWC[iListWC] and closestLat eq latListWC[iListWC] then begin

        ar_stats[iLon-sLon,iLat-sLat,iTime,iLevList,2,*] = 1 ; marks entire trajectory as landfalling AR

        ar_stats[iLon-sLon,iLat-sLat,iTime,iLevList,2,iStep] = 2 ; marks step of landfall

        LF_check = 1

        LF_step = iStep

        arStreakLF = 1

      endif

    endfor

  endif



  if iStep eq 0 then begin

    arStreak = 1

    if LF_check eq 1 then arStreakLF = 1

  endif else begin

    if arStreak ge 1 then arStreak += 1

    if LF_check eq 1 and arStreakLF ge 1 then arStreakLF += 1

  endelse

endif else begin

  if arStreak ge 1 then begin

    ar_stats[iLon-sLon,iLat-sLat,iTime,iLevList,1,0:arStreak-1] = 1

    arStreak = 0

  endif

  if arStreakLF ge 1 then begin

    if LF_step eq 0 then ar_stats[iLon-sLon,iLat-sLat,iTime,iLevList,3,LF_step:LF_step+arStreakLF-1] = 1

    if LF_step ne 0 then ar_stats[iLon-sLon,iLat-sLat,iTime,iLevList,3,LF_step:LF_step+arStreakLF-2] = 1

    arStreakLF = 0

  endif

endelse



; The 5th dimension of ar_stats is the parcel's yes/no "AR status":

; 0) is the parcel currently in an AR?

; 1) has the parcel been in an AR up to this point?

; 2) does the parcel make landfall in an AR?


; 3) if the parcel makes landfall in an AR, has it been in an AR up to this point



; calculate change in x, y, and z between this step and next

;------------------------------------------------------------



Here is the calculated change of parcel location



if tDir eq 1 then begin

  del_x = ((0-u_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep])*3600.*(nHour/(timeRatio*nXDay)))/1000.

  del_y = ((0-v_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep])*3600.*(nHour/(timeRatio*nXDay)))/1000.

  del_z = ((0-w_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep])*3600.*(nHour/(timeRatio*nXDay)))

endif

if tDir eq 2 then begin

  del_x = ((0+u_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep])*3600.*(nHour/(timeRatio*nXDay)))/1000.

  del_y = ((0+v_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep])*3600.*(nHour/(timeRatio*nXDay)))/1000.

  del_z = ((0+w_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep])*3600.*(nHour/(timeRatio*nXDay)))

endif



; calculate change in q and dr between this step and next

;---------------------------------------------------------

if iStep ne 0 then begin

  if tDir eq 1 then begin

  dq_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep] = $

      (q_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep]-q_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep-1])

  dr_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep] = $

      (dq_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep]/q_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep])*100.

  endif

  if tDir eq 2 then begin

  dq_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep-1] = $

      (q_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep-1]-q_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep])

  dr_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep-1] = $

      (dq_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep]/q_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep-1])*100.

  endif

endif



; calculate parcel position (x,y,z) at next step

;------------------------------------------------

if iStep ne nStep-1 then begin

  lon_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep+1] = lon_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep] + $

      del_x/((!PI/180.)*6370.*cos(lat_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep]*(!PI/180.)))

  lat_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep+1] = lat_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep] + del_y/111.2

  lev_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep+1] = lev_stats[iLon-sLon,iLat-sLat,iTime,iLevList,iStep] + del_z

endif



if tDir eq 1 then jTime -= 1


if tDir eq 2 then jTime += 1



      endfor ; iStep

    endfor ; iLevList



;************************************

  endif ; iList

endfor ; iList

;************************************



  endfor ; iLat

endfor ; iLon



;--------------------------------------------------------------------------------------------------;



        lastYearMon = strYear + strMon

      endif ; skip ne 0 

    endfor ; iTime



;--------------------------------------------------------------------------------------------------;

; Save data for each month                                                                         ;

;--------------------------------------------------------------------------------------------------;



trajDir = '/uufs/chpc.utah.edu/common/home/steenburgh-group4/jon/traj/data/parcel_trajectories/'

if tDir eq 1 and iYear ge 14 then trajDir = '/uufs/chpc.utah.edu/common/home/steenburgh-group1/jon/extra_traj/'

if tDir eq 2 and iYear ge 11 then trajDir = '/uufs/chpc.utah.edu/common/home/steenburgh-group1/jon/extra_traj/'

if tDir eq 1 then tStr = 'backward' else tStr = 'forward'



save, lon_stats, filename = trajDir + 'lon_stats_' + locStr + '_' + tStr + '_' + strtrim(yearmon,2)

save, lat_stats, filename = trajDir + 'lat_stats_' + locStr + '_' + tStr + '_' + strtrim(yearmon,2)

save, lev_stats, filename = trajDir + 'lev_stats_' + locStr + '_' + tStr + '_' + strtrim(yearmon,2)

save, q_stats,   filename = trajDir + 'q_stats_'   + locStr + '_' + tStr + '_' + strtrim(yearmon,2)

save, hw_stats,  filename = trajDir + 'hw_stats_'  + locStr + '_' + tStr + '_' + strtrim(yearmon,2)

;save, dq_stats,  filename = trajDir + 'dq_stats_'  + locStr + '_' + tStr + '_' + strtrim(yearmon,2)

;save, dr_stats,  filename = trajDir + 'dr_stats_'  + locStr + '_' + tStr + '_' + strtrim(yearmon,2)

save, ar_stats,  filename = trajDir + 'ar_stats_'  + locStr + '_' + tStr + '_' + strtrim(yearmon,2)



;--------------------------------------------------------------------------------------------------;



  endfor ; iMon

endfor ; iYear



;==================================================================================================;

;==================================================================================================;



END                                                                                ; End of Program



;==================================================================================================;


;==================================================================================================;