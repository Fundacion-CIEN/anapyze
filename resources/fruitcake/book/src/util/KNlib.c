
/********************************************************************************
Librer�a que contiene funciones espec�ficas para el c�lculo de 
los coeficientes de Klein-Nishina
paguiar Noviembre2004
***********************************************************************************/

#include <stdio.h>
#include <math.h>

#include <util/KNlib.h>

/*RADIO_PHOTON_ENERGY*/
/*Calcula la relacion entre la energia del foton antes/despues de la colision
E energ�a en eV del fot�n antes de la colisi�n
theta_rad �ngulo de dispersi�n en radianes*/
double ratio_photon_energy(double E,double theta_rad)
{
	double P; //resultado
	double me_c2,qe; //masa del electron por velocidad luz al cuadrado y carga electr�n
	double c,c2; //velocidad de la luz
	double A,f_ang; //calculos previos
	
	c=3e8;  // metros/segundo
	c2=c*c;
	qe=1.6e-19;
	me_c2=9.11e-31*c2/qe;  //viene de pasar eV->J
	A=E/me_c2; //constante en la f�rmula
	f_ang=1-cos(theta_rad);
	P=1/(1+(A*f_ang));
	return(P);
}

