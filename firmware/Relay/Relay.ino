
//VERSION: 20170706

#include <Thread.h>
#include <ThreadController.h>

// ThreadController that will controll all threads
ThreadController controll = ThreadController();

//read cmd Thread (as a pointer)
Thread* readcmdThread = new Thread();
//template 1 Thread
Thread* temp1Thread = new Thread();
int temp1TimeON = 10000; //sec
int temp1TimeOFF = 20000; //sec

#define ON LOW
#define OFF HIGH

// 繼電器(Relay) digi pin define
// digi pin 2=pin4, 3=pin5, 4=pin6,
//          5=pin11, 6=pin12, 7=pin13, 8=pin14
const int relayPin[] = {
  2, 3, 4, 5
};
//6, 11
int pinCount = 4;           // the number of pins

// 繼電器1~4狀態, LOW=Active
int relayState[] = {
  OFF, OFF, OFF, OFF
};

const int LINE_BUFFER_SIZE = 80; // max line length is one less than this

void setup() {
  // put your setup code here, to run once:
  // soft serial pin2 = Rx, pin3 = Tx
  Serial.begin(9600);               // 開啟 Serial port, 通訊速率為 9600 bps
  Serial.write("Power On");
  for (int thisPin = 0; thisPin < pinCount; thisPin++) {
    pinMode(relayPin[thisPin], OUTPUT); // 把 relayPin 設置成 OUTPUT
  }
  //delay(1000);
  //Test
  for (int thisPin = 0; thisPin < pinCount; thisPin++) {
    digitalWrite(relayPin[thisPin], ON);  //ON
    delay(1000);
    digitalWrite(relayPin[thisPin], OFF);  //OFF
    relayState[thisPin] = 1;
  }
  //thread
  readcmdThread->onRun(readcmdCallback);
  readcmdThread->setInterval(500);

  temp1Thread->enabled = false;
  temp1Thread->onRun(template1Callback);
  temp1Thread->setInterval(1000);
  // Adds threads to the controller
  controll.add(readcmdThread);

  Serial.write("System ready");
}
int getPower(int idx)
{
  if (idx > 3) {
    Serial.print("getPower out of index:");
    Serial.println(idx);
    return -1;
  }
  int val = digitalRead(relayPin[idx]);
  Serial.print("Power ");
  Serial.print(idx + 1);
  Serial.print(" status: ");
  state2Power(val);

}
void setPower(int idx, int state)
{
  if (state == 1 ) {
    relayState[idx] = 0; // 0= on
  } else {
    relayState[idx] = 1; // 1= off
  }
  digitalWrite(relayPin[idx], relayState[idx]);    // 讓繼電器作動, 切換開關
  Serial.print("Power " + String(idx + 1) + " status: ");      // 把繼電器的狀態印到 Serial Port
  state2Power(relayState[idx]);
}
void state2Power(int state)
{
  if (state == ON) {
    Serial.println("ON");
  } else {
    Serial.println("OFF");
  }
}
//idx = 0~3
void switchRelay(int idx)
{
  if (relayState[idx] == OFF)
    relayState[idx] = ON;                      // 把繼電器狀態改為 ON
  else
    relayState[idx] = OFF;                      // 把繼電器狀態改為 OFF

  digitalWrite(relayPin[idx], relayState[idx]);    // 讓繼電器作動, 切換開關
  Serial.print("Relay " + String(idx) + " status: ");        // 把繼電器的狀態印到 Serial Port
  Serial.println(relayState[idx]);

}
//printf like function (limit 128 chars)
void pf(const char *fmt, ... ) {
  char tmp[128]; // resulting string limited to 128 chars
  va_list args;
  va_start (args, fmt );
  vsnprintf(tmp, 128, fmt, args);
  va_end (args);
  Serial.print(tmp);
}

int read_line(char* buffer, int bufsize)
{
  for (int index = 0; index < bufsize; index++) {
    // Wait until characters are available
    while (Serial.available() == 0) {
    }

    char ch = Serial.read(); // read next character
    //Serial.print(ch); // echo it back: useful with the serial monitor (optional)

    if (ch == '\n') {
      buffer[index] = 0; // end of line reached: null terminate string
      return index; // success: return length of string (zero if string is empty)
    }

    buffer[index] = ch; // Append character to buffer
  }

  // Reached end of buffer, but have not seen the end-of-line yet.
  // Discard the rest of the line (safer than returning a partial line).

  char ch;
  do {
    // Wait until characters are available
    while (Serial.available() == 0) {
    }
    ch = Serial.read(); // read next character (and discard it)
    //Serial.print(ch); // echo it back
  } while (ch != '\n');

  buffer[0] = 0; // set buffer to empty string even though it should not be used
  return -1; // error: return negative one to indicate the input was too long
}
//=================================================================================
//TODO: pre-define ON/OFF loop?

void template1Callback()
{

}
//=================================================================================
void help()
{
  Serial.println("Only support \"set\" and \"get\" command");
}
void helpSetCMD()
{
  Serial.println("Set command:");
  Serial.println(" set <power num> <0/1>");
  Serial.println("<power num>: 1~4");
  Serial.println("<0:off/1:on>");
}
void helpGetCMD()
{
  Serial.println("Get command should be:");
  Serial.println(" get <power num> ");
  Serial.println("<power num>: 1~4");
}
//=================================================================================

void readcmdCallback() {
  // put your main code here, to run repeatedly:
  Serial.print("> ");
  // Read command
  // 檢查是否有資料可供讀取
  char line[LINE_BUFFER_SIZE];
  if (read_line(line, sizeof(line)) < 0) {
    Serial.println("Error: line too long");
    return; // skip command processing and try again on next iteration of loop
  }
  // Process command
  char cmd1, cmd2, cmd3;
  //Serial.print("Parsing the input string: ");// '%s'\n", input);
  //Serial.println(line);
  char *token = strtok(line, " ");
  int i = 0;
  char cmds[3];
  while (token) {
    //Serial.println(token);
    cmds[i] = token;
    token = strtok(NULL, " ");
    i++;
  }
  //Serial.println("==" + String(i) + "==========================");

  if (strcmp(cmds[0], "set") == 0) {
    //set relay on/off
    if (i < 3) {
      helpSetCMD();
      return;
    }
    //Serial.println("Set command");
    int p, s;
    p = atoi(cmds[1]);
    s = atoi(cmds[2]);
    setPower(p - 1, s);
  } else if (strcmp(cmds[0], "get") == 0) {
    //get relay status
    if (i < 2) {
      helpGetCMD();
      return;
    }
    //Serial.println("Get command");
    int p = atoi(cmds[1]);
    getPower(p - 1);
  } else if (strcmp(cmds[0], "temp1") == 0) {
    // enable/disable, power num, On sec , Off sec,

  } else if (strcmp(cmds[0], "") == 0) {
    help();
    return;
  } else {
    Serial.print("Error: unknown command: \"");
    Serial.print(line);
    Serial.println("\" (available commands: \"set\", \"get\")");
  }
  //delay(1000);

}
void loop() {
  // run ThreadController
  // this will check every thread inside ThreadController,
  // if it should run. If yes, he will run it;
  controll.run();

}
