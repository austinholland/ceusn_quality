#include <stdlib.h>
#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <math.h>
#include <fcntl.h>
#include <signal.h>
#include <curses.h>

#define MAXSTA 2500

/*****************************

        GLASS_netcape D. McNamara Jan. 2014

	code to calculate network capabilities for a list of GLASS stations
		Mw threshold 
 		detection time
		station-event distances

 	noise levels are computed from PQLX PSDPDF statistics.

	modified from: global_minmw
	code to calculate the global Mw threshold 
	for a list of stations.
	D.E. McNamara - March 2005
	modified from minmw.c
 	
******************************/

main( int argc, char **argv)

{

	char	*stafile, *this_program, ch;
	char	station[MAXSTA][6], netcode[MAXSTA][3], locode[MAXSTA][3], chan[MAXSTA][5];
	char	noisefile[20], fullnoisefile[200], stafcfile[100];
	int     n=0,k=0, minflag, i=0, numsta=0, nummw=0, mw_index, delta_index;
	int	numperiods=0, latinc=1, loninc=1;
	float	freq1, freq2, vel_stafc_db90, stafc_db90, startperiod, endperiod;
        float   stalat[MAXSTA], stalon[MAXSTA], evlat, evlon, delta, az;
        float   minlat, minlon, maxlat, maxlon, geom, stafc[MAXSTA], filtfc[MAXSTA];
        float   period, periods[100], db, fc, pi2=2.*3.1415927, beta=3.5, pi=3.1415927;
        float   pdfpow, min, max, db10, db80, db90, db90s[100], mean, median, ave, mode;
        float   noqamp, noqpowr, noqdb, spf;
        float   m0, r, sigma=100000000, distcm, mu=3e11, fcamp, ttimes[MAXSTA], distkm[MAXSTA];
	float	mw, detectmw, pvel=8.5;
	double	amp, powr;
        float   cn, q, atten, mindetect[MAXSTA];
	float	mws[10], fcs[10], deltas[20], fcmax[10][20];
        FILE    *pp, *fp, *ap, *lp, *hp, *op, *sp, *tp, *dp;

/* parse command line */
	if (argc < 2) {
                usage();
                exit(1);
        }
        this_program = argv[0];
        stafile = argv[1];

/* clean mindetect array */
	for (i=0; i<=500; i++)
                mindetect[i]=6.5;

/* whole globe  */
	minlat=-90;
	maxlat=90;
	minlon=-180;
	maxlon=180;

/* small caribean 
        minlat=-20;
        maxlat=40;
        minlon=-120;
        maxlon=-20;
*/
/* big caribean 
        minlat=-25;
        maxlat=45;
        minlon=-140;
        maxlon=-10;
*/

/* set some parameters - test box  
	minlat=40;
	maxlat=42;
	minlon=-120;
	maxlon=-118;
*/
/* China and Asia 
        minlat=0;
        maxlat=80;
        minlon=30;
        maxlon=160;
*/

/* small caribean 
        minlat=-20;
        maxlat=40;
        minlon=-120;
*/
/*  South America 
	minlat=-70;
	maxlat=20;
	minlon=-120;
	maxlon=-20;
*/

/* open output files */
        if ((op = fopen("minmw.out", "w")) == NULL) {
            usage();
            printf("\n\nUnable to open output file: minmw.out\n\n");
            exit(0);
        }
        if ((pp = fopen("db.out", "w")) == NULL) {
            usage();
            printf("\n\nUnable to open output file: db.out\n\n");
            exit(0);
        }
        if ((ap = fopen("minmw.sta", "w")) == NULL) {
            usage();
            printf("\n\nUnable to open output file: minmw.sta\n\n");
            exit(0);
        }
	if ((tp = fopen("proptime.out", "w")) == NULL) {
            usage();
            printf("\n\nUnable to open output file: proptime.sta\n\n");
            exit(0);
        }
	if ((dp = fopen("distances.out", "w")) == NULL) {
            usage();
            printf("\n\nUnable to open output file: proptime.sta\n\n");
            exit(0);
        }


/* open and read station file */
        if ((sp = fopen(stafile, "r")) == NULL) {
            usage();
            printf("\n\nUnable to open input file: %s\n\n",stafile);
            exit(0);
        }
/* read in station file */
	while (fscanf(sp,"%s %s %s %s %f %f %f", &station[numsta], &netcode[numsta], &locode[numsta], &chan[numsta], &stalat[numsta], &stalon[numsta], &stafc[numsta]) != EOF) {

           fprintf(ap, "%3.3f %3.3f %s %s %s %s %3.3f\n", stalat[numsta], stalon[numsta], netcode[numsta], station[numsta], locode[numsta], chan[numsta], stafc[numsta]);
/*
           printf("%3.3f %3.3f %s %s %s %s %3.3f\n", stalat[numsta], stalon[numsta], netcode[numsta], station[numsta], locode[numsta], chan[numsta], stafc[numsta]);
*/
	   numsta++;
	}

	    fclose(sp);
	    fclose(ap);

/* open and read fcsmap output and load arrays */
            if ((lp = fopen("newfcsamp.out", "r")) == NULL) {
                usage();
                printf("\n\nUnable to open input file: fcsamp.out\n\n");
                exit(0);
            }
            while ((ch = fgetc(lp)) != EOF) {
              ungetc(ch,lp);
              fscanf(lp,"%f %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f", &mws[nummw], &fcs[nummw], &fcmax[nummw][0],&fcmax[nummw][1], &fcmax[nummw][2], &fcmax[nummw][3], &fcmax[nummw][4], &fcmax[nummw][5], &fcmax[nummw][6], &fcmax[nummw][7], &fcmax[nummw][8], &fcmax[nummw][9], &fcmax[nummw][10], &fcmax[nummw][11], &fcmax[nummw][12], &fcmax[nummw][13], &fcmax[nummw][14], &fcmax[nummw][15]);
              nummw++;
            }
	    fclose(lp);
	    for (k=0; k<=15; k++) {
	      deltas[k]=2.0*k;
	    }



/* loop through lats and lons */
        latinc=2;
        loninc=2;
        for (evlat=minlat; evlat<=maxlat; evlat=evlat+latinc){
          for (evlon=minlon; evlon<=maxlon; evlon=evlon+loninc){

/* clean mindetect array */
       	     for (i=0; i<=500; i++)
                mindetect[i]=6.5;

/* loop through station array */
            for (i=0; i<=numsta-1; i++){
		minflag=0;
		delta_az(&evlat, &evlon, &stalat[i], &stalon[i], &delta, &az);

/* find and open station noisefile  to fill arrays*/
	      k=0;

	      sprintf(fullnoisefile, "/dbdata/mcnamara_home/PDF/GLASS/DailyStats/%1s.%3s.%2s.%3s.mod", netcode[i], station[i], locode[i], chan[i]);


              if ((hp = fopen(fullnoisefile, "r")) == NULL) {
                usage();
                printf("\n\nUnable to open input file: %s\n\n",fullnoisefile);
                exit(0);
              }

/*
printf("Station noise file exist: %s\n\n",fullnoisefile);
*/

	      while ((ch = fgetc(hp)) != EOF) {
                ungetc(ch,hp);
/* scanf for noise levels: fill db90s with median noise */
                fscanf(hp,"%f %f %f %f %f %f", &periods[k], &mean, &mode, &db10, &db90s[k], &db90);
		k++;
	      }
	      numperiods=k-2;
	      fclose(hp);
/* 
 loop through periods in 1/8 octave intervals
*/
	      startperiod=0.1;
	      startperiod=0.141421; /* 7Hz, GSN nyquist */
	      startperiod=0.03125;
              endperiod=128;
	      for (period=startperiod; period<=endperiod; period=period*pow(2.0,0.125)) {
		fc=1.0/period;
/* compute Mw for each fc */
	        r=2.34*beta/(pi2*fc);     /* fault size Brune, 1970 eq. 36, corrected 1971*/
                m0=2.29*sigma*pow((1e5*r),3); /* Brune 1970, moment eq# 31, corrected 1971 */
                mw=.667*log10(m0)-10.7;  /* Mw = moment mag. Kanimori(1977) */

/*
printf("%s %f %f %f %e\n", station, period, fc, mw, m0);
*/

/* compute amplitude at station */
	        distcm=111.19*delta*1e5;
	        distkm[i]=111.19*delta;
	        cn=1./(4.*mu*beta*1e7);


/* lookup effective station fc from fcsamp output
   station max amp is a function of Mw and delta.
   due to combination of: Brune model, attenuation and SP narrow band filter
*/
		delta_index=0;
	        for (k=0; k<=15; k++) {
	          if (delta>=deltas[k] && delta<deltas[k+1]) 
			delta_index=k;
	        }
		if (delta_index==0)
		  delta_index=15;
		mw_index=0;
		for (k=0; k<=nummw-1;k++){
	          if (mw>=mws[k] && mw<mws[k+1]) 
			mw_index=k;
		}
		if (mw_index==0)
		  mw_index=nummw-2;


/*
printf("%d %d\n", mw_index, delta_index);
printf("%f %f %f\n", mw, delta, fcmax[mw_index][delta_index]);
*/

/*  calculate amp using effective fc from NSNfilters 
    or stafc which is a function of nyquist at each station */
	      filtfc[i]=fcmax[mw_index][delta_index];
/* use the smaller of filtfc or stafc */
	      if (stafc[i] >= filtfc[i]) {
	        amp=cn*m0*filtfc[i]*pow(fc,2)/(pow(filtfc[i],2)+pow(fc,2))/distkm[i];
		stafc[i]=filtfc[i];
	      } else {
	        amp=cn*m0*stafc[i]*pow(fc,2)/(pow(stafc[i],2)+pow(fc,2))/distkm[i];
	      }


/* geometric spreading term */
	       geom=1.0/pow(distcm,0.5);
	       amp=amp*geom;

/* use central US Lg attenuation [Erickson et al 2004]*/
	         q=640.0*pow(stafc[i],0.35);

/* compute attenuation term */
	       atten=pow(2.7182818,((-1*pi*stafc[i]*distcm)/(q*beta*1e5)));
       	       amp=amp*atten;

/* Pwave amp is 10 times smaller than S */
/* correction for matching brune scaling to PSD calculation normalization */
	       amp=amp/6.0;

/* convert amp to powr */
	       powr=amp*amp;
	       if (powr==0.0){
		 db=-200;
		} else {
	         db=10.0*log10(powr);
		}

/* find new db90 for effective stafc */
	       for (k=0;k<=numperiods;k++) {
		freq1=1.0/periods[k];
		freq2=1.0/periods[k+1];
		if (stafc[i]<=freq1 && stafc[i]>=freq2) {
			stafc_db90=db90s[k];

/* convert stafc_db90 to velocity from acceleration */
 	        	vel_stafc_db90=stafc_db90-10*log10(stafc[i]*pi2);
/* flag bad noise levels */
                        if (vel_stafc_db90 < -170){
                           vel_stafc_db90=-99.1111;
                           stafc_db90=-99.1111;
                        }

/*
printf("IN IF %d %s %f %f %f %f %f %f\n", k, station[i], period, fc, stafc_db90, db90s[k], stafc[i], filtfc[i]);
printf("   %f \n", vel_stafc_db90);
*/


		}

	       }

/* find fc where db above the noise */
	       if (db>=vel_stafc_db90 && minflag==0) {
		 mindetect[i]=mw;

/*
printf(" HERE    %f %f %f\n", db, fc, mindetect[i]);
*/

  		minflag=1;
	      }

	    } /* end loop throug periods in 1/8 octave intervals */


fprintf(pp,"%s %f %f %f %f %f\n", station[i], distkm[i], powr, mindetect[i], evlat, evlon);


/* calculate travel time to stations */
	if (distkm[i]<150) {
          pvel=5.5;
        } else {
          pvel=8.1;
        }
        ttimes[i]=distkm[i]/pvel;

	    } /* end for loop through stations */

/* sort mindetect array and find 9th element */
	    bubble(mindetect, i);
	    bubble(ttimes, i);
	    bubble(distkm, i);


/* output 9 elements of minmw, ttimes, distkm for propagation time map*/

	    fprintf(op," %6.3f %6.3f %5.2f %5.2f %5.2f %5.2f %5.2f %5.2f %5.2f %5.2f %5.2f \n", evlat, evlon, mindetect[0], mindetect[1], mindetect[2], mindetect[3], mindetect[4], mindetect[5], mindetect[6], mindetect[7], mindetect[8]);
	    printf(" %6.3f %6.3f %5.2f %5.2f %5.2f %5.2f %5.2f %5.2f %5.2f %5.2f %5.2f \n", evlat, evlon, mindetect[0], mindetect[1], mindetect[2], mindetect[3], mindetect[4], mindetect[5], mindetect[6], mindetect[7], mindetect[8]);

	    fprintf(tp, "%6.3f %6.3f %6.4f %6.4f %6.4f %6.4f %6.4f %6.4f %6.4f %6.4f %6.4f\n", evlat, evlon, ttimes[0], ttimes[1], ttimes[2], ttimes[3], ttimes[4], ttimes[5], ttimes[6], ttimes[7], ttimes[8]);
	    printf("%6.3f %6.3f %6.4f %6.4f %6.4f %6.4f %6.4f %6.4f %6.4f %6.4f %6.4f\n", evlat, evlon, ttimes[0], ttimes[1], ttimes[2], ttimes[3], ttimes[4], ttimes[5], ttimes[6], ttimes[7], ttimes[8]);
	    fprintf(dp, "%6.3f %6.3f %6.4f %6.4f %6.4f %6.4f %6.4f %6.4f %6.4f %6.4f %6.4f \n", evlat, evlon, distkm[0], distkm[1], distkm[2], distkm[3], distkm[4], distkm[5], distkm[6], distkm[7], distkm[8]);
	    printf( "%6.3f %6.3f %6.4f %6.4f %6.4f %6.4f %6.4f %6.4f %6.4f %6.4f %6.4f \n", evlat, evlon, distkm[0], distkm[1], distkm[2], distkm[3], distkm[4], distkm[5], distkm[6], distkm[7], distkm[8]);

	  } /* end for evlon */
	}  /* end for evlat */

	fclose(op);
	fclose(tp);
	fclose(dp);


} /* end main */

usage()
{
        fprintf(stderr,"\nUSAGE: minmw stafile\n\n");
}

/*
 * function to calculate the great circle distance and back azimuth (azimuth
 * clockwise from north between two points on a sphere with a flattening of
 * 1/295)
 *
 * returns the azimuth from point a to point b, measured from north
 * 
 * all IO is in degrees
 * 
 */

#include <math.h>

double          flat = 1.0000000;
double          rad;

#define cl 0			/* subscripts for sine and cosine arrays */
#define sl 1
#define cn 2
#define sn 3

double          cdif;


delta_az(alati, aloni, blati, bloni, delta, baz)
	float          *alati, *aloni, *blati, *bloni, *delta, *baz;
{
	double          a[4], b[4];
	double          alat, alon, blat, blon;

	rad = 3.14159265358979323846 / 180;

	alat = (double) *alati;
	alon = (double) *aloni;
	blat = (double) *blati;
	blon = (double) *bloni;

	dbpt(alat, alon, a);
	dbpt(blat, blon, b);

	cdif = b[cn] * a[cn] + b[sn] * a[sn];
	*delta = acos(a[sl] * b[sl] * cdif + a[cl] * b[cl]) / rad;

	*baz = atan2((a[cn] * b[sn] - b[cn] * a[sn]) * b[sl], a[sl] * b[cl] - a[cl] * cdif * b[sl]);
	*baz /= rad;
	if (*baz < 0)
		*baz += 360;

}

double          maxDegree = 360;

dbpt(lat, lon, a)
	double          lat, lon, a[4];
{
	a[cl] = 1;
	if (abs(lat != 90))
		a[cl] = sin(atan(flat * tan(lat * rad)));
	a[sl] = sqrt(1 - a[cl] * a[cl]);
	a[sn] = sin(lon * rad);

	cdif = fmod(lon, maxDegree);
	if (cdif < 0)
		cdif *= -1;

	a[cn] = sqrt(1 - a[sn] * a[sn]);
	if (cdif > 90 && cdif < 270)
		a[cn] *= -1;

}

bubble (a, n)
int     n;
float   a[];
{
        int     i, j;

        for (i = 0; i < n - 1; ++i)
          for (j = n - 1; i < j; --j)
            order(&a[j-1], &a[j]);

}  /* end bubble */

order (p, q)
float   *p, *q;
{
        float   temp;

        if (*p > *q) {
           temp = *p;
           *p = *q;
           *q = temp;
        }
} /* end order */
