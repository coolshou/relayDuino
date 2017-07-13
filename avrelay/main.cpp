#include "usbasp_uart.h"
#include "version.h"

#include <unistd.h>
#include <chrono>
#include <fstream>
#include <thread>
#include <vector>
#include <stdlib.h>                     // for atoi, EXIT_SUCCESS
#include <string.h>                     //for strdup
#include <sstream>

int verbose=0;

//read to \n
void readline(USBasp_UART* usbasp)
{
	bool b=true;
	while(b){
		uint8_t buff[300];
		int rv=usbasp_uart_read(usbasp, buff, sizeof(buff));
		if(rv<0){
			fprintf(stderr, "read: rv=%d\n", rv);
			return;
		}
		for(int i=0;i<rv;i++){
			printf("%c",buff[i]);
		}
		fflush(stdout);
		if (strchr((char*)buff, 10)) {  // found \n
			//fprintf(stderr, "found new line %c\n", buff[0]);
			b=false;
		}
	}
}

void read_usbasp(USBasp_UART* usbasp){
	uint8_t buff[300];
	int rv=usbasp_uart_read(usbasp, buff, sizeof(buff));
	if(rv<0){
		fprintf(stderr, "read: rv=%d\n", rv);
		return;
	}
	for(int i=0;i<rv;i++){
		printf("%c",buff[i]);
	}
	fflush(stdout);
}

void showVersion() {
	fprintf(stderr, "Version: %s\n", VERSION);
}
void usageSet(const char* name, bool bShowName) {
	if (bShowName) {
		fprintf(stderr, "Usage:\n %s", name);
	}
	fprintf(stderr, " -s <pin> <1/0> \tset power pin ON(1)/OFF(0)\n");
}
void usage(const char* name){
	showVersion();
	fprintf(stderr, "Usage: %s [OPTIONS]\n", name);
	fprintf(stderr, "Control Power Pin On/Off through USBasp+.\n");
	fprintf(stderr, "Options:\n");
	fprintf(stderr, " -g <pin> \t\tget power pin status\n");
	usageSet(name, false);
	fprintf(stderr, " -m \t\t\tget max supported power pin number\n");
	fprintf(stderr, " -d <num> \t\tincrease debug verbosity\n");
	fprintf(stderr, " -v \t\tshow version\n");
	fprintf(stderr, " -h \t\tshow this help\n");
	exit(0);
}

int main(int argc, char** argv){
	if(argc==1){
		usage(argv[0]);
	}
	int iPowerPin=0; //
	long iPowerSwitch=0; // 0: OFF, 1: ON
	char *next;

	int baud=9600;
	int parity=USBASP_UART_PARITY_NONE;
	int bits=USBASP_UART_BYTES_8B;
	int stop=USBASP_UART_STOP_1BIT;

	bool bDoGet = false;
	bool bDoSet = false;
	bool bGetMaxPowerNum = false;

	opterr=0;
	int c;

	while( (c=getopt(argc, argv, "vhmd:g:s:"))!=-1){
		switch(c){
		case 'g':  //get power pin
			bDoGet = true;
			iPowerPin = atoi(optarg);
			break;
		case 's': //set power pin ON/OFF
			bDoSet = true;
			if(argc!=4){
				usageSet(argv[0] , true);
				exit(-1);
			}
			optind--;
			for( ;optind < argc && *argv[optind] != '-'; optind++){
				if (optind==2) { 		//power pin
					iPowerPin = atoi(argv[optind]);
				}
				if (optind==3) { 		//power switch
					//iPowerSwitch = atoi(argv[optind]);  //if a to i fail, it will return 0
					iPowerSwitch = strtol(argv[optind], &next, 10);
					if ((next == argv[optind]) || (*next != '\0') || ( iPowerSwitch <0) || ( iPowerSwitch >1)) {
						usageSet(argv[0] , true);
						exit(-1);
					}
				}
				//fprintf(stderr,"optind: %d  %s \n",optind ,argv[optind]);
			}
			break;
		case 'm':
			bGetMaxPowerNum = true;
			break;
		case 'v':
			showVersion();
			exit(0);
			break;
		case 'h':
			usage(argv[0]);
			exit(0);
			break;
		case 'd':
			verbose++;
			break;

		default:
			usage(argv[0]);
			exit(EXIT_FAILURE);
		}
	}
  USBasp_UART usbasp;
  try {
    int rv;
    if((rv=usbasp_uart_config(&usbasp, baud, parity | bits | stop)) < 0){
      fprintf(stderr, "Error %d while initializing USBasp\n", rv);
      if(rv==USBASP_NO_CAPS){
        fprintf(stderr, "USBasp has no UART capabilities.\n");
      }
      return -1;
    }
  }catch(...) {
    fprintf(stderr, "Error no USBASP+\n");
    return -1;
  }
	std::stringstream ss;
	std::string s ;
	if (bDoGet) { 	//get power
		ss << "get " << iPowerPin << "\n" ;
		s = ss.str();
	}
	if (bDoSet) { 	//set power
		ss << "set " << iPowerPin << " " << iPowerSwitch << " \n" ;
		s = ss.str();
	}
	if (bGetMaxPowerNum) { //get Max support power number
		ss << "max" << " \n" ;
		s = ss.str();
	}
	if (s.length() >0) {
		//send command to USBasp+
  	//fprintf(stderr, "cmd:  %s\n", s.c_str());
		usbasp_uart_write_all(&usbasp, (uint8_t*)s.c_str(), s.length());
		//read result
		readline(&usbasp);
	}

	return EXIT_SUCCESS;
}
