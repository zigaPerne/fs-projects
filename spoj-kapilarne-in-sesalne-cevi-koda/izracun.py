#1. Input data: geometric and operating conditions.
#2. Calculate the adiabatic mass flow rate (Eq. (9)) using hi,c as the enthalpy path
#3. Based on the calculated mass mass flow rate, calculate:
	#a. Number of transfer units (Eq. (15));
	#b. Heat exchanger effectiveness (Eq. (12));
	#c. Suction line outlet temperature (Eq. (11));
	#d. Refrigerant enthalpy at the evaporator inlet (Eq. (10));
	#e. Average enthalpy (Eq. (17)).
#4. Calculate the adiabatic mass flow rate (Eq. (9)) using the
#refrigerant average enthalpy.
#5. Calculate the K-multiplier (Eq. (16)) and correct the mass flow

import numpy as np
import CoolProp.CoolProp as cool


def izracun(t, hladivo, prt):
	
	# Podatki za 2. tocko algoritma:
	D_c	= t[1]*10**(-3)	# Premer kapilarne cevi			[m]
	D_s	= t[2]*10**(-3)	# Premer sesalne cevi			[m] 
	p_c	= t[3]*10**5	# Tlak na inlet				[Pa]
	p_e	= t[4]*10**5	# Tlak uplinjanja			[Pa] 
	dt_sub 	= t[5]		# Podhlajenje				[K] 

	fi	= 6.0		# Kapilarna konstanta			[/]
	L_c	= 2.7		# Dolzina kapilarne cevi		[m]
	L_s	= 1.5		# Dolzina sesalne cevi			[m]
	

	# Podatki za 3. tocko algoritma:
	t_s_i	= 273.15 + t[7] # Temperatura na vstopu v sesalno cev	[K] 

	c	= 4		# Konstanta				[/] 		
	n	= 0.405		# Konstanta				[/] 		
	

	# Konstante za korekcijo masnega toka:
	c0 	= 1.103
	c1	= 0.3
	c2	= -0.03
	c3	= -0.450
	c4	= -0.2

	
	
	
	#2. Calculate the adiabatic mass flow rate (Eq. (9)) using hi,c as the enthalpy path
	
	# Podatki za vstop v zanko - se spreminjajo vsako iteracijo
	t_sat 	= cool.PropsSI("T", "Q", 0, "P", p_c, hladivo)			# Temperatura nasicene tekocine na kondenzatorju 
	t_c_i	= t_sat - dt_sub						# Temperatura na vstopu v kapilaro
	h_c_i 	= cool.PropsSI("H", "T", t_c_i, "P", p_c, hladivo)		# Entalpija  na vstopu v kapilaro
	t_s_o	= t_s_i + 30							# Začetni priblizek izstopne temperrature iz sesalne cevi
	p_i 	= p_c								# Tlak na vhodu v kapilarno cev (enak tlaku kondenzacije) 
	h_avg 	= h_c_i								# Prvotna definicija h_avg (to racunamo z zanko) 
	
	
	# Definicija spremenljivk za izvedbo iteracije
	w 	= 3 / 3600
	i 	= 0
	K 	= 1
	
	while(abs(K) > 1e-8 ): 
		i = i+1
		
		h_f 	= h_avg							# Entalpiji na vstopu v kapilaro 
		t_f 	= cool.PropsSI("T", "H", h_f, "P", p_c, hladivo)	# Temperatura na flash-point
		p_f	= cool.PropsSI("P", "Q", 0, "T", t_f, hladivo)		# Tlak na flash-point
		v_f	= 1 / (cool.PropsSI("D", "P", p_f, "Q", 0, hladivo))	# Specificni volumen na Flash-Point
		eta_f	= cool.PropsSI("V", "P", p_f, "Q", 0, hladivo)		# Viskoznost na flash-point
										
		k = 1.63e5 * p_f**(-0.72)					#
		a = v_f * (1 - k)						# Koeficienti
		b = v_f * p_f * k						# 
		
		# Izracun masnega toka:
		w_prev 	= w	
		w = fi * np.sqrt((D_c**5 / L_c) * (((p_i - p_f) / v_f) + ((p_f - p_e) / a) + ((b / a**2) * np.log((a * p_e + b) / (a * p_f + b))))) 
		
		t_s_avg = (t_s_i + t_s_o) / 2						# Povprečna temperatura v sesalni cevi 	[K]
		lam_v 	= cool.PropsSI("L", "H", h_avg, "P", p_e, hladivo)		# Termična prevodnost-nasicena tekocina [W/mK] 		
		eta_v 	= cool.PropsSI("V", "H", h_avg, "P", p_e, hladivo)		# Viskoznost-nasicena tekocina		[Pa s]
		c_p_v 	= cool.PropsSI("C", "H", h_avg, "P", p_e, hladivo)		# Specifična toplota-nasicena tekocina	[J/kgK] 
		v_v	= 1 / (cool.PropsSI("D", "H", h_avg, "P", p_e, hladivo))	# Specifični volumen-nasicena tekocina	[m3/kg]
		c_p_s 	= cool.PropsSI("C", "P", p_e, "T", t_s_avg, hladivo)		# Specifična toplota v sesalni cevi	[J/kgK]
		
		#3. Based on the calculated mass mass flow rate, calculate:
			#a. Number of transfer units (Eq. (15));
			#b. Heat exchanger effectiveness (Eq. (12));
			#c. Suction line outlet temperature (Eq. (11));
			#d. Refrigerant enthalpy at the evaporator inlet (Eq. (10));
			#e. Average enthalpy (Eq. (17)).
		
		NTU = (c * w**(n - 1) * L_s * lam_v**(2/3)) / (D_s**n * eta_v**(n - (1/3)) * c_p_v**(2/3))	# Number of Transfer Units
		eps = NTU / (1 + NTU)										# Ucinkovitost prenosnika toplote
		t_s_o = t_s_i + eps * (t_c_i - t_s_i)								# Temperatura na izstopu iz sesalne cevi
		h_c_o = h_c_i - eps * c_p_s * (t_c_i - t_s_i) 							# Entalpija na izstopu iz kapilare
		
	
		h_avg = 0.5 * (h_c_i + h_c_o) 
		K = 1 - (w_prev / w)





		if(prt == 1): 
			print("Iteracija", i) 
			print("Masni tok =", w * 3600) 
			print("K_multiplier =", K) 
			print("c_p_s", c_p_s) 
			print("tlak", p_f * 10**(-5))
			print("v_f", v_f)
			print("razlika", t_s_o - t_s_i) 
			print("eps", eps) 
			print("tso", t_s_o) 
			print("\n") 
		


	w 	= c0 * (L_s / L_c)**(c1) * (D_s / D_c)**(c2) * eps**c3 * ((v_f * eta_f) / (v_v * eta_v))**(c4) * w	


	return np.array([i, t_s_o  - 273.15, w * 3600, eps])   


