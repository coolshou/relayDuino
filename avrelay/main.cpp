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

void writeTest(USBasp_UART* usbasp, int size){
	std::string s;
	char c='a';
	for(int i=0; i<size; i++){
		s+=c;
		c++;
		if(c>'z'){ c='a'; }
	}
	auto start=std::chrono::high_resolution_clock::now();
	int rv;
	if((rv=usbasp_uart_write_all(usbasp, (uint8_t*)s.c_str(), s.size()))<0){
		fprintf(stderr, "Error %d while writing...\n", rv);
		return;
	}
	auto finish=std::chrono::high_resolution_clock::now();
	auto us=std::chrono::duration_cast<std::chrono::microseconds>(finish-start).count();
	printf("%zu bytes sent in %zums\n", s.size(), us/1000);
	printf("Average speed: %lf kB/s\n", s.size()/1000.0/(us/1000000.0));
}

void readTest(USBasp_UART* usbasp, size_t size){
	auto start=std::chrono::high_resolution_clock::now();
	int us;
	std::string s;
	while(1){
		if(s.size()==0){
			start=std::chrono::high_resolution_clock::now();
		}
		if(s.size()>=size){
			auto finish=std::chrono::high_resolution_clock::now();
			us=std::chrono::duration_cast<std::chrono::microseconds>(finish-start).count();
			break;
		}
		uint8_t buff[300];
		int rv=usbasp_uart_read(usbasp, buff, sizeof(buff));
		if(rv==0){ continue; } // Nothing is available for now.
		else if(rv<0){
			fprintf(stderr, "Error while reading, rv=%d\n", rv);
			return;
		}
		else{
			s+=std::string((char*)buff, rv);
			fprintf(stderr, "%zu/%zu\n", s.size(), size);
		}
	}
	printf("Whole received text:\n");
	printf("%s\n", s.c_str());
	printf("%zu bytes received in %dms\n", s.size(), us/1000);
	printf("Average speed: %lf kB/s\n", s.size()/1000.0/(us/1000000.0));
}

void read_forever(USBasp_UART* usbasp){
	while(1){
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
}
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

void write_forever(USBasp_UART* usbasp){
	uint8_t buff[1024];
	while(1){
		int rv=read(STDIN_FILENO, buff, sizeof(buff));
		if(rv==0){ return; }
		else if(rv<0){
			fprintf(stderr, "write: read from stdin returned %d\n", rv);
			return;
		}
		else{
			usbasp_uart_write_all(usbasp, buff, rv);
		}
	}
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

	opterr=0;
	int c;

	while( (c=getopt(argc, argv, "vhd:g:s:"))!=-1){
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
		case 'v':
			showVersion();
			exit(0);
			break;
		case 'h':
			usage(argv[0]);
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
	int rv;
	if((rv=usbasp_uart_config(&usbasp, baud, parity | bits | stop)) < 0){
		fprintf(stderr, "Error %d while initializing USBasp\n", rv);
		if(rv==USBASP_NO_CAPS){
			fprintf(stderr, "USBasp has no UART capabilities.\n");
		}
		return -1;
	}
	//TODO:
	if (bDoGet) { 	//get power
		//fprintf(stderr, "get Power %d state\n",iPowerPin );
		std::stringstream ss;
		ss << "get " << iPowerPin << "\n" ;
		std::string s = ss.str();
		//fprintf(stderr, "cmd:  %s\n", s.c_str());
		//send command to USBasp+
		usbasp_uart_write_all(&usbasp, (uint8_t*)s.c_str(), s.length());
		//read result
		readline(&usbasp);
	}
	//set power
	if (bDoSet) {
		//fprintf(stderr, "set Power %d state to %ld\n",iPowerPin, iPowerSwitch );
		std::stringstream ss;
		ss << "set " << iPowerPin << " " << iPowerSwitch << " \n" ;
		std::string s = ss.str();
		//fprintf(stderr, "cmd:  %s\n", s.c_str());
		//send command to USBasp+
		usbasp_uart_write_all(&usbasp, (uint8_t*)s.c_str(), s.length());
		//read result
		readline(&usbasp);
	}
	return EXIT_SUCCESS;
}
