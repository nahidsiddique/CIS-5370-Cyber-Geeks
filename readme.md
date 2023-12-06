To Run the Simulation of FDI Attack and Impact Analysis – Please follow the steps-  

	1.Open “DCFastCharger.slx” or simulation file from evcs/matlab_simulation and run it. 
	2.Change the directory to FDI_Attack_and_Impact 
	3.Run docker-compose file with  1. dcbuild 2.dcup 
	4.Open for different terminal and excess the container- ev-1, evcs-2, attacker-1, malicious-router-1 with docksh <container name> 
	5.For ev-1 and evcs-2 change the directory to – evfile and evcsfile 
	6.For attacker-1 and malicious-router-1 change the directory to – cd volume 
	7.Run the icmp.py file from attacker-1 container 
	8.Run charging_point.py from ev-1 , central_server.py from evcs-2 and mitm_tcp.py from malicious-router-1 
	9.In ev-1 terminal, provide the first input from these keywords [ApplicationReset', 'FirmwareUpdate', 'LocalReset', 'PowerUp', 'RemoteReset', 'ScheduledReset', 'Triggered', 'Unknown', 'Watchdog] and second input from 0-100.  
	10.Users can able to see the communication messeges between ev-1 and evcs-2 
 	11.From attacker-1 run the attack_soc.py file from volumes directory. 
	12.Open “DCFastChargerExample.m” or  simulation file from evcs/matlab_simulation and run it. 

 

 
Hybrid encryption contains two Python files named ev.py and central_server.py. ev.py is for Electric vehicles to send encrypted messages to the central_server. central_server.py is for servers to receive the encrypted messages from the EVs and decrypt them. 

	1.To run ev.py we need to use the syntax: python3 ev.py 127.0.0.1 8888  where We are passing the server IP address and port number of the server while running the ev.py.  

	2.On the other hand, the syntax to run central_server.py : python3 central_server.py 8888 Here central server is waiting for connections on the specified port number. 

 