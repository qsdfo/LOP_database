/**
*
*  @file			needleman.c
*  @brief			Optimized Needleman-Wunsch alignment with homopolymers handling
*
*	This file contains the implementation of the optimized Needleman-Wunsch alignment algorithm with homopolymers handling
*
*  @author			Philippe Esling
*	@version		1.1
*	@date			16-01-2013
*  @copyright		UNIGE - GEN/EV (Pawlowski) - 2013
*	@licence		MIT Media Licence
*
*/

#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include <math.h>

#define U_FEPS 1.192e-6F          /* 1.0F + E_FEPS != 1.0F */
#define U_DEPS 2.22e-15           /* 1.0 +  E_DEPS != 1.0  */

// #define _PRINT_COOR     printf("X pos : %i   Y pos : %i   cursor : %i\n", xpos, ypos, cursor);
#define _PRINT_COOR ;
#define E_FPEQ(a,b,e) (((b - e) < a) && (a < (b + e)))

#define _DIAG 	0
#define _UP  	1
#define _LEFT 	2

#define BUFFSIZE	4096
#define SEQSIZE		1024

#define PITCH_DIM     5
#define NUM_PITCH_CLASS     12

// Debug
#define LEN 10
#define BUF_SIZE 32  // Long size

struct needle_state {
    PyObject *error;
};

#if PY_MAJOR_VERSION >= 3
#define GETSTATE(m) ((struct needle_state*)PyModule_GetState(m))
#else
#define GETSTATE(m) (&_state)
static struct needle_state _state;
#endif

char *int2bin(long a, char *buffer, int buf_size) {
    int i;
    for (i = buf_size-1; i >= 0; i--) {
        buffer[i] = (a & 0x1) + '0';
        a >>= 1;
    }

    return buffer;
}

int score_chord(long ax, long bx){
    int a = (int) ax;
    int b = (int) bx;
    float score = 0;
    // char buffer[BUF_SIZE];
    // buffer[BUF_SIZE - 1] = '\0';
    int nb_elt_a = 0;
    int nb_elt_b = 0;
    int i;

    // int a_print = (int)a;
    // int b_print = (int)b;

    if((a==0)||(b==0)){
        // If one part is a silence, cost 0
        score = 0;
    }
    else
    {
        for (i=0; i < NUM_PITCH_CLASS; i++)
        {
            nb_elt_a += (a & 0x1);
            nb_elt_b += (b & 0x1);
            if((a & 0x1) & (b & 0x1))
            {
                score += 1;
            }
            else if( ((a & 0x1) & !(b & 0x1) ) | ( (!(a & 0x1)) & (b & 0x1) ) ){
                // Mismatch
                score -= 1;
            }
            a = a >> 1;
            b = b >> 1;
        }
    }
    float nEl = ceil((float)(nb_elt_a + nb_elt_b) / 2.0f);
    score /= (nEl > 0 ? nEl : 1);
    score *= 5;

    // Print
    // printf("a = %i\n", a_print);
    // printf("b = %i\n", b_print);
    // printf("nb_elt_a = %i    nb_elt_b = %i    nEl = %f\n", nb_elt_a, nb_elt_b, nEl);
    // int2bin(a_print, buffer, BUF_SIZE - 1);
    // printf("Binary representation of a : %s\n", buffer);
    // int2bin(b_print, buffer, BUF_SIZE - 1);
    // printf("Binary representation of b : %s\n", buffer);
    // printf("Score : %f\n", score);

    return (int)score;
}

static float getScore(const int *horizGap_m, const int *vertGap_m, const int *m, int lena, int lenb, int *start1, int *start2, int noEndGap_n){
    int i,j, cursor;
    float score = INT_MIN;
    *start1 = lena-1;
    *start2 = lenb-1;

    if(noEndGap_n)
    {
        cursor = lena * lenb - 1;
        if(m[cursor]>horizGap_m[cursor]&&m[cursor]>vertGap_m[cursor])
        score = m[cursor];
        else if(horizGap_m[cursor]>vertGap_m[cursor])
        score = horizGap_m[cursor];
        else
        score = vertGap_m[cursor];
    }
    else {

        for (i = 0; i < lenb; ++i)
        {
            cursor = (lena - 1) * lenb + i;
            if(m[cursor]>score)
            {
                *start2 = i;
                score = m[cursor];
            }
            if(horizGap_m[cursor]>score)
            {
                score = horizGap_m[cursor];
                *start2 = i;
            }
            if(vertGap_m[cursor]>score)
            {
                score = vertGap_m[cursor];
                *start2 = i;
            }
        }

        for (j = 0; j < lena; ++j)
        {
            cursor = j * lenb + lenb - 1;
            if(m[cursor]>score)
            {
                *start1 = j;
                *start2 = lenb-1;
                score = m[cursor];
            }
            if(horizGap_m[cursor]>score)
            {
                score = horizGap_m[cursor];
                *start1 = j;
                *start2 = lenb-1;
            }
            if(vertGap_m[cursor]>score)
            {
                score = vertGap_m[cursor];
                *start1 = j;
                *start2 = lenb-1;
            }
        }
    }
    return score;
}

void homopolHandling(int type, char a, char b, int homoPol, int *homopolState, char *matching, int *stats, int addDist, int nbAligns)
{
    int		i,j;

    switch (type)
    {
        case _UP:
        if (a == homopolState[0])
        {
            homopolState[1] += 1;
            homopolState[2] += addDist;
            homopolState[5] += addDist;
        }
        else
        {
            if (homopolState[1] >= homoPol && homopolState[4] >= homoPol && homopolState[2] != 0)
            {
                stats[4] -= homopolState[2];
                stats[0] += homopolState[2];
                for (i = 2; i < 2 + homopolState[1] && nbAligns - i >= 0; i++)
                matching[nbAligns - i] = 'h';
                homopolState[4] -= 10e5;
            }
            homopolState[0] = a;
            homopolState[1] = 1;
            homopolState[2] = addDist;
            if (homopolState[4] >= homoPol && homopolState[1] >= homoPol && homopolState[5] != 0)
            {
                stats[4] -= homopolState[5];
                stats[0] += homopolState[5];
                for (i = 2; i < i + homopolState[4] && nbAligns - i >= 0; i++)
                matching[nbAligns - i] = 'h';
                homopolState[1] -= 10e5;
            }
            homopolState[3] = '-';
            homopolState[4] = 0;
            homopolState[5] = addDist;

        }
        break;
        case _LEFT:
        if (b == homopolState[3])
        {
            homopolState[2] += addDist;
            homopolState[4] += 1;
            homopolState[5] += addDist;
        }
        else
        {
            if (homopolState[4] >= homoPol && homopolState[1] >= homoPol && homopolState[5] != 0)
            {
                stats[4] -= homopolState[5];
                stats[0] += homopolState[5];
                for (j = 2; j < 2 + homopolState[4] && nbAligns - j >= 0; j++)
                matching[nbAligns - j] = 'h';
                homopolState[1] -= 10e5;
            }
            homopolState[3] = b;
            homopolState[4] = 1;
            homopolState[5] = addDist;
            if (homopolState[1] >= homoPol && homopolState[4] >= homoPol && homopolState[2] != 0)
            {
                stats[4] -= homopolState[2];
                stats[0] += homopolState[2];
                for (j = 2; j < 2 + homopolState[1] && nbAligns - j >= 0; j++)
                matching[nbAligns - j] = 'h';
                homopolState[4] -= 10e5;
            }
            homopolState[0] = '-';
            homopolState[1] = 0;
            homopolState[2] = addDist;
        }
        break;
        case _DIAG:
        if (homoPol > 0)
        {
            if (homopolState[0] != a)
            {
                if (homopolState[1] >= homoPol && homopolState[4] >= homoPol && homopolState[2] != 0)
                {
                    stats[4] -= homopolState[2];
                    stats[0] += homopolState[2];
                    for (j = 2; j < 2 + homopolState[1] && nbAligns - j >= 0; j++)
                    matching[nbAligns - j] = 'h';
                    homopolState[4] -= 10e5;
                }
                homopolState[0] = a;
                homopolState[1] = 1;
                homopolState[2] = 0;
            }
            else
            {
                if (a == b)
                homopolState[1] += 1;
                else
                {
                    if (homopolState[1] >= homoPol && homopolState[4] >= homoPol && homopolState[2] != 0)
                    {
                        stats[4] -= homopolState[2];
                        stats[0] += homopolState[2];
                        for (j = 2; j < 2 + homopolState[1] && nbAligns - j >= 0; j++)
                        matching[nbAligns - j] = 'h';
                        homopolState[4] -= 10e5;
                    }
                    homopolState[1] -= 10e5;
                    homopolState[4] -= 10e5;
                }
            }
            if (homopolState[3] != b)
            {
                if (homopolState[4] >= homoPol && homopolState[1] >= homoPol && homopolState[5] > 0)
                {
                    stats[4] -= homopolState[5];
                    stats[0] += homopolState[5];
                    for (j = 2; j < 2 + homopolState[4] && nbAligns - j >= 0; j++)
                    matching[nbAligns - j] = 'h';
                    homopolState[1] -= 10e5;
                }
                homopolState[3] = b;
                homopolState[4] = 1;
                homopolState[5] = 0;
            }
            else
            {
                if (a == b)
                homopolState[4] += 1;
                else
                {
                    if (homopolState[4] >= homoPol && homopolState[1] >= homoPol && homopolState[5] > 0)
                    {
                        stats[4] -= homopolState[5];
                        stats[0] += homopolState[5];
                        for (j = 2; j < 2 + homopolState[4] && nbAligns - j >= 0; j++)
                        matching[nbAligns - j] = 'h';
                        homopolState[1] -= 10e5;
                    }
                    homopolState[4] -= 10e5;
                    homopolState[1] -= 10e5;
                }
            }
        }
        break;
        default:
        return;
    }
}

float *needlemanWunsch(const long  *a, const long  *b,
    int         lena, int         lenb,
    long        *trace_a, long        *trace_b,
    int         gapopen,
    int         gapextend){
        int homoPol = 0;
        int verbose = 1;
        int oneGap = 0;

        // Tuning parameters
        int     noEndGap_n = 1;
        int     endgapopen = 0;
        int     endgapextend = 0;

        int     curMalloc = lena * lenb;
        int     *m = malloc(curMalloc * sizeof(int));
        int     *horizGap_m = malloc(curMalloc * sizeof(int));
        int     *vertGap_m = malloc(curMalloc * sizeof(int));
        int     *trBack = malloc(curMalloc * sizeof(int));

        int		xpos, ypos;
        int		match;
        long    bconvcode;
        int		horizGap_mp;
        int		vertGap_mp;
        int		mp;
        int		i, j;
        int		cursor = 0, cursorp;
        int		*start1, *start2;
        char	*matching = NULL;
        int		testog;
        int		testeg;
        int		lastGap = 0;
        int		nbEndGap = 0;
        // int     bestSoFar;
        /* Align stats : nbId, F, nbGaps, F, nbDiffs, F */
        int		stats[6] = {0, 0, 0, 0, 0, 0};
        int 	homopolState[6] = {'?', 0, 0, '?', 0, 0};
        // Output
        int		nbAligns = 0;
        static float   output[4] = {0.0, 0.0, 0.0, 0.0};

        // printf("Lena : %i   Lenb : %i\n\n", lena, lenb);

        if (noEndGap_n == 1)
        {
            endgapopen = 0;
            endgapextend = 0;
        }
        start1 = calloc(1, sizeof(int));
        start2 = calloc(1, sizeof(int));
        horizGap_m[0] = -endgapopen-gapopen;
        vertGap_m[0] = -endgapopen-gapopen;
        m[0] = score_chord(a[0], b[0]);
        /* First initialise the first column */
        for (ypos = 1; ypos < lena; ++ypos)
        {
            // printf("posa : %d - posb : 0\n", ypos);
            match = score_chord(a[ypos], b[0]);
            cursor = ypos * lenb;
            cursorp = cursor - lenb;
            testog = m[cursorp] - gapopen;
            testeg = vertGap_m[cursorp] - gapextend;
            vertGap_m[cursor] = (testog >= testeg ? testog : testeg);
            m[cursor] = match - (endgapopen + (ypos - 1) * endgapextend);
            //
            _PRINT_COOR
            //
            horizGap_m[cursor] = - endgapopen - ypos * endgapextend - gapopen;
        }
        horizGap_m[cursor] -= endgapopen - gapopen;
        for (xpos = 1; xpos < lenb; ++xpos)
        {
            // printf("posa : 0 - posb : %d\n", xpos);
            match = score_chord(a[0], b[xpos]);
            cursor = xpos;
            cursorp = xpos -1;
            testog = m[cursorp] - gapopen;
            testeg = horizGap_m[cursorp] - gapextend;
            horizGap_m[cursor] = (testog >= testeg ? testog : testeg);
            m[cursor] = match - (endgapopen + (xpos - 1) * endgapextend);
            //
            _PRINT_COOR
            //
            vertGap_m[cursor] = -endgapopen - xpos * endgapextend -gapopen;
        }
        vertGap_m[cursor] -= endgapopen - gapopen;
        xpos = 1;
        /*
        * Filling step
        */
        while (xpos != lenb)
        {
            ypos = 1;
            bconvcode = b[xpos];
            cursorp = xpos-1;
            cursor = xpos++;
            // bestSoFar = INT_MAX;
            while (ypos < lena)
            {
                // printf("posa : %d - posb : %d\n", ypos, bconvcode);
                match = score_chord(a[ypos++], bconvcode);
                cursor += lenb;
                mp = m[cursorp];
                horizGap_mp = horizGap_m[cursorp];
                vertGap_mp = vertGap_m[cursorp];
                if(mp > horizGap_mp && mp > vertGap_mp){
                    m[cursor] = mp+match;
                    //
                    _PRINT_COOR
                    //
                }
                else if(horizGap_mp > vertGap_mp){
                    m[cursor] = horizGap_mp+match;
                    //
                    _PRINT_COOR
                    //
                }
                else{
                    m[cursor] = vertGap_mp+match;
                    //
                    _PRINT_COOR
                    //
                }
                if(xpos==lenb)
                {
                    testog = m[++cursorp] - endgapopen;
                    testeg = vertGap_m[cursorp] - endgapextend;
                }
                else
                {
                    testog = m[++cursorp];
                    if (testog<horizGap_m[cursorp])
                    testog = horizGap_m[cursorp];
                    testog -= gapopen;
                    testeg = vertGap_m[cursorp] - gapextend;
                }
                if(testog > testeg)
                vertGap_m[cursor] = testog;
                else
                vertGap_m[cursor] = testeg;
                cursorp += lenb;
                if(ypos==lena)
                {
                    testog = m[--cursorp] - endgapopen;
                    testeg = horizGap_m[cursorp] - endgapextend;
                }
                else
                {
                    testog = m[--cursorp];
                    if (testog<vertGap_m[cursorp])
                    testog = vertGap_m[cursorp];
                    testog -= gapopen;
                    testeg = horizGap_m[cursorp] - gapextend;
                }
                if (testog > testeg)
                horizGap_m[cursor] = testog;
                else
                horizGap_m[cursor] = testeg;
            }
        }
        output[1] = getScore(horizGap_m, vertGap_m, m, lena, lenb, start1, start2, noEndGap_n);
        xpos = *start2;
        ypos = *start1;
        cursorp = 0;


        /* PROMPT */
        // printf("### Match matrix \n");
        // for(int i=0; i<lena*lenb;i++)
        // {
        //     printf("%i; ", m[i]);
        //     if((i+1) % (lenb) == 0)
        //     {
        //         printf("\n");
        //     }
        // }

        // printf("### horizGap matrix \n");
        // for(int i=0; i<lena*lenb;i++)
        // {
        //     printf("%i; ", horizGap_m[i]);
        //     if((i+1) % (lenb) == 0)
        //     {
        //         printf("\n");
        //     }
        // }
        //
        // printf("### verticGap matrix \n");
        // for(int i=0; i<lena*lenb;i++)
        // {
        //     printf("%i; ", vertGap_m[i]);
        //     if((i+1) % (lenb) == 0)
        //     {
        //         printf("\n");
        //     }
        // }

        /*
        * Trace-back step
        */
        // printf("position beginning : x: %i y: %i\n", xpos, ypos);
        while (xpos>=0 && ypos>=0)
        {
            cursor = ypos*lenb+xpos;
            mp = m[cursor];
            // Gap extend horizontal
            // Le premier test sert à déterminer si on est ou non sur un bord (haut ou bas)
            if(cursorp == _LEFT && E_FPEQ((ypos==0||(ypos==lena)?
            endgapextend:gapextend), (horizGap_m[cursor]-horizGap_m[cursor+1]),U_FEPS))
            {
                trBack[cursor] = _LEFT;
                xpos--;
            }
            // Gap extend vertical
            // Le premier test sert à déterminer si on est ou non sur un bord (gauche ou droite)
            else if(cursorp== _UP && E_FPEQ((xpos==0||(xpos==lenb)?
            endgapextend:gapextend), (vertGap_m[cursor]-vertGap_m[cursor+lenb]),U_FEPS))
            {
                trBack[cursor] = _UP;
                ypos--;
            }
            else if(mp >= horizGap_m[cursor] && mp >= vertGap_m[cursor])
            {
                if(cursorp == _LEFT && E_FPEQ(mp,horizGap_m[cursor],U_FEPS))
                {
                    trBack[cursor] = _LEFT;
                    xpos--;
                }
                else if(cursorp == _UP && E_FPEQ(mp,vertGap_m[cursor],U_FEPS))
                {
                    trBack[cursor] = _UP;
                    ypos--;
                }
                else
                {
                    trBack[cursor] = 0;
                    ypos--;
                    xpos--;
                }
            }
            else if(horizGap_m[cursor]>=vertGap_m[cursor] && xpos>-1)
            {
                trBack[cursor] = _LEFT;
                xpos--;
            }
            else if(ypos>-1)
            {
                trBack[cursor] = _UP;
                ypos--;
            }
            cursorp = trBack[cursor];
        }
        // printf("\n");

        xpos = *start2;
        ypos = *start1;

        if (verbose != 0)
        {
            matching = malloc((lenb + lena) * sizeof(char));
        }
        for (i = lenb - 1; i > xpos;)
        {
            stats[2]++;
            stats[4] += 1 - noEndGap_n;
            nbEndGap++;
            /*		stats[0] += noEndGap_n;*/
            if (verbose)
            {
                trace_a[nbAligns] = 0;
                trace_b[nbAligns] = 1;
                matching[nbAligns] = (noEndGap_n ? 'e' : ' ');
            }
            nbAligns++; i--;
            if (homoPol > 0)
            homopolHandling(_LEFT,b[i + 1],b[i + 1], homoPol, homopolState, matching, stats, noEndGap_n, nbAligns);
        }
        for (j = lena - 1; j > ypos;)
        {
            stats[2]++;
            stats[4] += 1 - noEndGap_n;
            nbEndGap++;
            if (verbose)
            {
                trace_a[nbAligns] = 1;
                trace_b[nbAligns] = 0;
                matching[nbAligns] = (noEndGap_n ? 'e' : ' ');
            }
            j--; nbAligns++;
            if (homoPol > 0)
            homopolHandling(_UP,a[j + 1],a[j + 1], homoPol, homopolState, matching, stats, noEndGap_n, nbAligns);
        }
        while (xpos >= 0 && ypos >= 0)
        {
            cursor = ypos * lenb + xpos;
            switch (trBack[cursor])
            {
                case _DIAG:
                lastGap = 0;
                mp = (a[ypos] == b[xpos]);
                stats[0] += (mp ? 1 : 0);
                stats[4] += (mp ? 0 : 1);
                if (verbose)
                {
                    trace_a[nbAligns] = 1;
                    trace_b[nbAligns] = 1;
                    matching[nbAligns] = (mp ? '|' : '.');
                }
                ypos--; xpos--; nbAligns++;
                if (homoPol > 0)
                homopolHandling(_DIAG,a[ypos + 1],b[xpos + 1], homoPol, homopolState, matching, stats, mp, nbAligns);
                break;
                case _LEFT:
                stats[2]++;
                /*stats[0] += (ypos == (lena - 1)	&& noEndGap_n ? 1 : 0);*/
                stats[4] += (ypos == (lena - 1)	&& noEndGap_n ? 0 : (lastGap && oneGap ? 0 : 1));
                if (ypos == (lena - 1))
                nbEndGap++;
                if (verbose)
                {
                    trace_a[nbAligns] = 0;
                    trace_b[nbAligns] = 1;
                    matching[nbAligns] = (ypos == (lena - 1) && noEndGap_n ? 'e' : (lastGap && oneGap ? 'c' : ' '));
                }
                xpos--; nbAligns++;
                lastGap = 1;
                if (homoPol > 0)
                homopolHandling(_LEFT,b[xpos + 1],b[xpos + 1], homoPol, homopolState, matching, stats, (lastGap && oneGap ? 0 : 1), nbAligns);
                break;
                case _UP:
                stats[2]++;
                /*stats[0] += (xpos == (lenb - 1) && noEndGap_n ? 1 : 0);*/
                stats[4] += (xpos == (lenb - 1) && noEndGap_n ? 0 : (lastGap && oneGap ? 0 : 1));
                if (xpos == (lenb - 1))
                nbEndGap++;
                if (verbose)
                {
                    trace_a[nbAligns] = 1;
                    trace_b[nbAligns] = 0;
                    matching[nbAligns] = (xpos == (lenb - 1) && noEndGap_n ? 'e' : (lastGap && oneGap ? 'c' : ' '));
                }
                ypos--; nbAligns++;
                lastGap = 1;
                if (homoPol > 0)
                homopolHandling(_UP,a[ypos + 1],a[ypos + 1], homoPol, homopolState, matching, stats, (lastGap && oneGap ? 0 : 1), nbAligns);
                break;
                default:
                break;
            }
        }

        // Complète en longeant les bords si une séquence s'est finie plus vite que l'autre
        for (; xpos >= 0 ; xpos--)
        {
            stats[2]++;
            stats[4] += 1 - noEndGap_n;
            nbEndGap++;
            /*stats[0] += noEndGap_n;*/
            if (verbose)
            {
                trace_a[nbAligns] = 0;
                trace_b[nbAligns] = 1;
                matching[nbAligns] = (noEndGap_n ? 'e' : ' ');
            }
            nbAligns++;
            if (homoPol > 0)
            homopolHandling(_LEFT,b[xpos],b[xpos], homoPol, homopolState, matching, stats, 1 - noEndGap_n, nbAligns);
        }

        for (; ypos >= 0; ypos--)
        {
            stats[2]++;
            stats[4] += 1 - noEndGap_n;
            nbEndGap++;
            /*stats[0] += noEndGap_n;*/
            if (verbose)
            {
                trace_a[nbAligns] = 1;
                trace_b[nbAligns] = 0;
                matching[nbAligns] = (noEndGap_n ? 'e' : ' ');
            }
            nbAligns++;
            if (homoPol > 0)
            homopolHandling(_UP,a[ypos],a[ypos], homoPol, homopolState, matching, stats, 1 - noEndGap_n, nbAligns);
        }

        // for(int i=0; i<nbAligns; i++){
        //     printf("%li; ", trace_a[i]);
        // }
        // printf("\n");
        // for(int i=0; i<nbAligns; i++){
        //     printf("%li; ", trace_b[i]);
        // }
        // printf("\n");
        ////////////////////////////////////////////////////////////////
        ////////////////////////////////////////////////////////////////
        ////////////////////////////////////////////////////////////////

        if (verbose)
        {
            free(matching);
        }
        free(start1);
        free(start2);
        free(m);
        free(horizGap_m);
        free(vertGap_m);
        free(trBack);

        // Last index gives the size of the traces
        output[0] = nbAligns;
        output[2] = stats[0];
        output[3] = stats[2];

        return output;
}

/* ################################################ */
/* Python interface */
static PyObject	*needleman_chord(PyObject* self, PyObject* args)
    {
    int i;
    // Input
    PyObject    *alist_PY; /* the list of int */
    PyObject    *blist_PY;
    int         gapopen;
    int         gapextend;
    // One element in a or b (needed for parsing a and b)
    PyObject    *intObj;
    // Python list converted to long list
    long        *alist;
    long        *blist;
    // Lists lenght
    int         lena;
    int         lenb;

    // Output C function
    float       *output;
    int         trace_length;
    int         sum_score;
    int         nbId;
    int         nbGaps;
    // Trace indexes for warping the tracks
    long        *trace_a;
    long        *trace_b;
    // Converted in Python object
    PyObject    *trace_a_PY; /* the list of int */
    PyObject    *trace_b_PY;

    // Get input value from python script
    if (!PyArg_ParseTuple(args, "OOii", &alist_PY, &blist_PY, &gapopen, &gapextend))
    {
        printf("Bad format for argument\n");
        return NULL;
    }

    /* get the number of lines passed to us */
    lena = (int) PyList_Size(alist_PY);
    if (lena < 0)   return NULL; /* Not a list */
    lenb = (int) PyList_Size(blist_PY);
    if (lenb < 0)   return NULL; /* Not a list */

    // Initialize alist and blist
    alist = calloc(lena, sizeof(long));
    blist = calloc(lenb, sizeof(long));
    // Trace_a and trace_b
    trace_a = calloc((lena+lenb), sizeof(long));
    trace_b = calloc((lena+lenb), sizeof(long));

    // Build int lists
    /* iterate over items of the list, grabbing strings, and parsing
    for numbers */
    for (i=0; i<lena; i++){
        /* grab the string object from the next element of the list */
        intObj = PyList_GetItem(alist_PY, i); /* Can't fail */
        Py_INCREF(intObj);
        /* make it a string */
        alist[i] = PyLong_AsLong(intObj);
        /* now do the parsing */
        Py_DECREF(intObj);
    }

    for (i=0; i<lenb; i++){
        /* grab the string object from the next element of the list */
        intObj = PyList_GetItem(blist_PY, i); /* Can't fail */
        Py_INCREF(intObj);
        /* make it a string */
        blist[i] = PyLong_AsLong(intObj);
        /* now do the parsing */
        Py_DECREF(intObj);
    }

    // Call function
    output = needlemanWunsch(alist, blist, lena, lenb, trace_a, trace_b, gapopen, gapextend);

    trace_length = (int)output[0];
    sum_score = (int)output[1];
    nbId = (int)output[2];
    nbGaps = (int)output[3];

    trace_a_PY = PyList_New(trace_length);
    if (!trace_a_PY){
        return NULL;
    }
    for (i = 0; i < trace_length; i++) {
        // Index are lenb+lena-i to flip lr the list and return only useful part
        intObj = PyLong_FromLong(trace_a[i]);
        if (!intObj) {
            Py_DECREF(trace_a_PY);
            return NULL;
        }
        // Be carreful with order : new element is added at (trace_length-i)
        PyList_SET_ITEM(trace_a_PY, i, intObj);
        Py_DECREF(intObj);
    }

    trace_b_PY = PyList_New(trace_length);
    if (!trace_b_PY){
        return NULL;
    }
    for (i = 0; i < trace_length; i++) {
        intObj = PyLong_FromLong(trace_b[i]);
        if (!intObj) {
            Py_DECREF(trace_b_PY);
            return NULL;
        }
        PyList_SET_ITEM(trace_b_PY, i, intObj);
        Py_DECREF(intObj);
    }

    // Free static output
    // free(output);
    free(alist);
    free(blist);
    free(trace_a);
    free(trace_b);

    // Convert to python value output
    return Py_BuildValue("OOiii", trace_a_PY, trace_b_PY, sum_score, nbId, nbGaps);
}

static PyMethodDef needle_methods[] = {
    {"needleman_chord", (PyCFunction)needleman_chord, METH_NOARGS, NULL},
    {NULL, NULL}
};

#if PY_MAJOR_VERSION >= 3

static int needle_traverse(PyObject *m, visitproc visit, void *arg) {
    Py_VISIT(GETSTATE(m)->error);
    return 0;
}

static int needle_clear(PyObject *m) {
    Py_CLEAR(GETSTATE(m)->error);
    return 0;
}


static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "needleman_chord",
        NULL,
        sizeof(struct needle_state),
        needle_methods,
        NULL,
        needle_traverse,
        needle_clear,
        NULL
};

#define INITERROR return NULL

PyMODINIT_FUNC
PyInit_needleman_chord(void)

#else
#define INITERROR return

void
initneedleman_chord(void)
#endif
{
#if PY_MAJOR_VERSION >= 3
    PyObject *module = PyModule_Create(&moduledef);
#else
    PyObject *module = Py_InitModule("needleman_chord", needle_methods);
#endif

    if (module == NULL)
        INITERROR;
    struct needle_state *st = GETSTATE(module);

    st->error = PyErr_NewException("needleman_chord.Error", NULL, NULL);
    if (st->error == NULL) {
        Py_DECREF(module);
        INITERROR;
    }

#if PY_MAJOR_VERSION >= 3
    return module;
#endif
}

/* ################################################ */
/* DEBUG */
// int main(){
//
//     int res;
//
//     long a[12] = {1,1,1,2,2,2,4,4,4,8,8,8};
//     long b[9] = {1,1,1,2,2,4,4,8,8};
//
//     int lena = 12;
//     int lenb = 9;
//
//     long *trace_a = calloc(lena + lenb, sizeof(long));
//     long *trace_b = calloc(lena + lenb, sizeof(long));
//
//     res = needlemanWunsch(a, b, lena, lenb, trace_a, trace_b,
//         3, 1);
//
//     int counter = 0;
//     for(int i=1; i<res+1; i++){
//         if(trace_a[res-i])
//         {
//             printf("%li; ", a[counter]);
//             counter++;
//         }
//         else{
//             printf("-; ");
//         }
//     }
//     printf("\n");
//     counter = 0;
//     for(int i=1; i<res+1; i++){
//         if(trace_b[res-i])
//         {
//             printf("%li; ", b[counter]);
//             counter++;
//         }
//         else{
//             printf("-; ");
//         }
//     }
//
//     return 0;
// }
