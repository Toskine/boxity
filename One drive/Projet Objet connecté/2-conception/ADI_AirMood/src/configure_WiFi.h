/*
  description : to configure the wifi, we can read EEPROM and try to connnect. If it fail, turn on hotspot.
  date : version du 27/01/2022
  auteur : robin/simon


  ce qu'il reste à faire :


  à corriger :
    - quand on appuis sur entrer lorsqu'on rentre le password, on retourne sur la première page.
    - mettre l'HTML dans un fichier à part et l'appeler ici.

*/

#include <ESP8266WiFi.h>
#include <ESPAsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <DNSServer.h>
#include <EEPROM.h>

extern String STAT;
bool SSID_received = false;
bool password_received = false;
String configure_WiFi_STATUS = "INIT";
String hot_spot_STATUS = "INIT";
String user_SSID;
String password;
String html_options_SSID = "";
String index_html;

#define configure_WiFi_TIMEOUT 1000 * 300 //
#define connecting_WiFi_TIMEOUT 1000 * 10 // 10 s

#define SSID_lenght user_SSID.length()
#define password_lenght password.length()
#define SSID_EEPROM_INDEX 0
#define password_EEPROM_INDEX SSID_EEPROM_INDEX + SSID_lenght
#define EEPROM_ASSIGNMENT 64
#define UNIT_SEPARATOR 0

String index_html_1 = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Objet connecté</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
  <div class="topnav">
    <h1>Connecte ton Objet connecté !</h1>
  </div>
  <div class="content">
    <div class="card-grid">
      <div class="card">
        <form action="/get">
          <p>
              <br>
              Veuillez choisir le WIFI : 
              <br>
)rawliteral";

String index_html_2 = R"rawliteral(
    <br>
          </p>
        </form>
      </div>
    </div>
  </div>
  
  <style>
html {
  font-family: Arial, Helvetica, sans-serif; 
  display: inline-block; 
  text-align: center;
}

h1 {
  font-size: 2.4rem; 
  color: white;
}

p { 
  font-size: 1.7rem;
}

.topnav { 
  overflow: hidden; 
  background-color: #142149;
}

body {  
  margin: 0;
}

.content { 
  padding: 7%;
}

.card-grid { 
  max-width: 1000px; 
  margin: 0 auto; 
  display: grid; 
  grid-gap: 3rem; 
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}

.card { 
  background-color: white; 
  box-shadow: 2px 2px 15px 1px rgba(140,140,140,.5);
}

input[type=submit] {
  border: none;
  color: #FEFCFB;
  background-color: #034078;
  padding: 15px 15px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 20px;
  width: 200px;
  margin-right: 10px;
  margin-top: 40px;
  border-radius: 4px;
  transition-duration: 0.4s;
  }

input[type=submit]:hover {
  background-color: #1282A2;
}

input[type=text], input[type=password], select {
  width: 60%;
  padding: 12px 20px;
  margin: 18px;
  font-size: 16px;
  display: inline-block;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
}

  </style>
</body></html>
)rawliteral";

String index_html_bis = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Objet connecté</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
  <div class="topnav">
    <h1>Connecte ton Objet connecté !</h1>
  </div>
  <div class="content">
    <div class="card-grid">
      <div class="card">
        <form action="/get">
          <p>
              <br>
              Mot de passe : <input type="password" name="password">
              <br>
              <input name='bouton' type="submit" value="Soumettre">
              <input name='bouton' type="submit" value="Retour">              
          </p>
        </form>
      </div>
    </div>
  </div>
  
  <style>
html {
  font-family: Arial, Helvetica, sans-serif; 
  display: inline-block; 
  text-align: center;
}

h1 {
  font-size: 2.4rem; 
  color: white;
}

p { 
  font-size: 1.7rem;
}

.topnav { 
  overflow: hidden; 
  background-color: #142149;
}

body {  
  margin: 0;
}

.content { 
  padding: 7%;
}

.card-grid { 
  max-width: 1000px; 
  margin: 0 auto; 
  display: grid; 
  grid-gap: 3rem; 
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}

.card { 
  background-color: white; 
  box-shadow: 2px 2px 15px 1px rgba(140,140,140,.5);
}

input[type=submit] {
  border: none;
  color: #FEFCFB;
  background-color: #034078;
  padding: 15px 15px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 20px;
  width: 200px;
  margin-right: 10px;
  margin-top: 40px;
  border-radius: 4px;
  transition-duration: 0.4s;
  }

input[type=submit]:hover {
  background-color: #1282A2;
}

input[type=text], input[type=password], select {
  width: 60%;
  padding: 12px 20px;
  margin: 18px;
  font-size: 16px;
  display: inline-block;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
}

  </style>
</body></html>
)rawliteral";

String index_html_bos_bis = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Objet connecté</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
  <div class="topnav">
    <h1>Connecte ton Objet connecté !</h1>
  </div>
  <div class="content">
    <div class="card-grid">
      <div class="card">
        <form action="/get">
          <p>
              <br>
              <h2>Merci</h2><br>
              <h3>L'objet va tenter de se connecter...</h3><br>
              <br>
          </p>
        </form>
      </div>
    </div>
  </div>
  
  <style>
html {
  font-family: Arial, Helvetica, sans-serif; 
  display: inline-block; 
  text-align: center;
}

h1 {
  font-size: 2.4rem; 
  color: white;
}

h2 {
  font-size: 2.4rem; 
  color: #142149;
}

h2 {
  font-size: 2.4rem; 
  color: #142149;
}

p { 
  font-size: 1.7rem;
}

.topnav { 
  overflow: hidden; 
  background-color: #142149;
}

body {  
  margin: 0;
}

.content { 
  padding: 7%;
}

.card-grid { 
  max-width: 1000px; 
  margin: 0 auto; 
  display: grid; 
  grid-gap: 3rem; 
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}

.card { 
  background-color: white; 
  box-shadow: 2px 2px 15px 1px rgba(140,140,140,.5);
}

input[type=submit] {
  border: none;
  color: #FEFCFB;
  background-color: #034078;
  padding: 15px 15px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 20px;
  width: 200px;
  margin-right: 10px;
  margin-top: 40px;
  border-radius: 4px;
  transition-duration: 0.4s;
  }

input[type=submit]:hover {
  background-color: #1282A2;
}

input[type=text], input[type=password], select {
  width: 60%;
  padding: 12px 20px;
  margin: 18px;
  font-size: 16px;
  display: inline-block;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
}

  </style>
</body></html>
)rawliteral";

DNSServer dnsServer;
AsyncWebServer server(80);

void search_Wifi(bool debug)
{

  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  // cherche tous les wifi dispos et les renvoit sous la forme [wifi1,wifi2,...]
  const int n = WiFi.scanNetworks(/*async=*/false, /*hidden=*/true);
  String list_wifi[n];

  int nbr = n;

  for (int i = 0; i < n; ++i)
  {
    list_wifi[i] = WiFi.SSID(i).c_str();
  }
  // Supprimer les doublons
  for (int i = 0; i < nbr; i++)
  {
    for (int j = i + 1; j < nbr;)
    {
      if (list_wifi[j] == list_wifi[i] or list_wifi[j] == "")
      {
        for (int k = j; k < nbr; k++)
        {
          list_wifi[k] = list_wifi[k + 1];
        }
        nbr--;
      }
      else
        j++;
    }
  }

  String list_wifi_wod[nbr];
  html_options_SSID = "";
  for (int i = 0; i < nbr; i++)
  {
    list_wifi_wod[i] = list_wifi[i];
    //<input type="submit" value="%OPTION15%>%OPTION15%"><br>
    html_options_SSID += "      <input name='SSID' type='submit' value='" + list_wifi_wod[i] + "'><br>" + "\n";
  }

  if (debug)
  {
    Serial.println();
    Serial.println("scanNetworks sucess");
    Serial.println("  wifi found : " + String(nbr));
    Serial.println("  List_wifi : hidden ");
    /*
    for (int i = 0; i < nbr; ++i)
    {
      Serial.println("    - " + list_wifi_wod[i]);
    }
    */
  }
}

void prepare_html(bool debug)
{
  index_html = index_html_1 + html_options_SSID + index_html_2;
  if (debug)
  {
    Serial.println();
    Serial.println("index_html : hidden");
    // Serial.println(index_html);
  }
}

void WiFiSoftAPSetup(String SSID, bool debug)
{
  // fonction qui met l'ESP en mode ACCESS POINT, permet qu'un appareil puisse s'y connecter
  WiFi.mode(WIFI_AP);
  WiFi.softAP(SSID);
  if (debug)
  {
    Serial.println();
    Serial.println("WiFi mode ACCESS POINT activated");
    Serial.print("  SSID : ");
    Serial.println(SSID);
    Serial.print("  AP IP address : ");
    Serial.println(WiFi.softAPIP());
  }
}

class CaptiveRequestHandler : public AsyncWebHandler
{
public:
  CaptiveRequestHandler() {}
  virtual ~CaptiveRequestHandler() {}

  bool canHandle(AsyncWebServerRequest *request)
  {
    // request->addInterestingHeader("ANY");
    return true;
  }

  void handleRequest(AsyncWebServerRequest *request)
  {
    request->send(200, "text/html", index_html);
  }
};

void setupServer(bool debug)
{
  if (debug)
  {
    Serial.println();
    Serial.println("Setting up Async WebServer");
  }
  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request)
            {
      request->send(200, "text/html", index_html); 
      Serial.println("Client Connected"); });

  server.on("/get", HTTP_GET, [](AsyncWebServerRequest *request)
            {
      String inputMessage;
      String inputParam;
      String bouton;
  
      if (request->hasParam("SSID")) {
        inputMessage = request->getParam("SSID")->value();
        inputParam = "SSID";
        user_SSID = inputMessage;
        SSID_received = true;
      }

      if (request->hasParam("password")) {
        inputMessage = request->getParam("password")->value();
        inputParam = "password";
        password = inputMessage;
        password_received = true;

      }

      if (request->hasParam("bouton")) {
        inputMessage = request->getParam("bouton")->value();
        inputParam = "bouton";
        bouton = inputMessage;
        if (bouton=="Retour"){SSID_received=false;password_received=false;}
      }

      if (!SSID_received and !password_received)
      {
      request->send(200, "text/html", index_html);
      }
      if (SSID_received and !password_received)
      {
      request->send(200, "text/html", index_html_bis);
      }
      if (SSID_received and password_received)
      {
      request->send(200, "text/html", index_html_bos_bis);
      } });
}

String hotspot_status = "init";

void hot_spot_run(bool debug)
{
  if (!SSID_received or !password_received)
  {
    dnsServer.processNextRequest();
  }
  else if (SSID_received and password_received)
  {
    STAT = "TRYING_CONNECTION";
    hotspot_status = "init";
    if (debug)
    {
      Serial.println();
      Serial.println("Data received from User :");
      Serial.println("  SSID = " + user_SSID);
      Serial.println("  password = " + password);
    }
  }
}

void hot_spot_begin(bool debug)
{
  if (STAT == "HOTSPOT_RUNNING" and hotspot_status == "init")
  {
    search_Wifi(debug);
    WiFiSoftAPSetup("ADI AirMood", debug);
    prepare_html(debug);
    setupServer(debug);
    dnsServer.start(53, "*", WiFi.softAPIP());
    server.addHandler(new CaptiveRequestHandler()).setFilter(ON_AP_FILTER); // only when requested from AP
    // more handlers...
    server.begin();
    if (debug)
    {
      Serial.println("Waiting for client connection...");
    }
    hotspot_status = "HOTSPOT_RUNNING";
  }
  else if (STAT == "HOTSPOT_RUNNING" and hotspot_status == "HOTSPOT_RUNNING")
  {
    hot_spot_run(debug);
  }
}
unsigned long t1 = millis();
String wifi_try_connection_status = "init";

void wifi_try_connection(bool debug)
{
  if (STAT == "TRYING_CONNECTION" and wifi_try_connection_status == "init")
  {
    t1 = millis();
    if (debug)
    {
      Serial.println();
      Serial.println("wifi_try_connection");
      Serial.println("  wifi_SSID : " + user_SSID);
      Serial.println("  wifi_password : " + password);
    }

    WiFi.mode(WIFI_STA);
    WiFi.begin(user_SSID.c_str(), password.c_str());
    wifi_try_connection_status = "CONNECTING";
  }
  else if (STAT == "TRYING_CONNECTION" and wifi_try_connection_status == "CONNECTING")
  {
    if (WiFi.status() == WL_CONNECTED)
    {
      STAT = "TRYING_CONNECTION_SUCCESS";
      wifi_try_connection_status = "init";
      // ecrire dans EEPROM
    }
    else if (millis() - t1 >= connecting_WiFi_TIMEOUT)
    {
      STAT = "CONNECTION_TIMEOUT";
      wifi_try_connection_status = "init";
    }
  }
}

void init_EEPROM(bool debug)
{
  EEPROM.begin(EEPROM_ASSIGNMENT);
}

void reset_EEPROM(bool debug)
{
  for (int i = 0; i < EEPROM_ASSIGNMENT; i++)
  {
    EEPROM.write(i, 0);
  }
  if (EEPROM.commit() and debug)
  {
    Serial.println("reset_EEPROM SUCCESS");
  }

  delay(500);
}

unsigned int count = 1;

void write_EEPROM(bool debug)
{

  if (debug)
  {
    Serial.println("  wifi_SSID : " + user_SSID);
    Serial.println("  wifi_password : " + password);
  }

  const char *c1 = user_SSID.c_str();
  const char *c2 = password.c_str();
  unsigned int i = 0;
  unsigned int j = 0;

  while (j < user_SSID.length())
  {
    EEPROM.put(j, c1[i]);
    i++;
    j++;
  }
  EEPROM.put(j, UNIT_SEPARATOR);
  j++;
  i = 0;
  while (j < user_SSID.length() + password.length() + 1)
  {
    EEPROM.put(j, c2[i]);
    i++;
    j++;
  }

  EEPROM.put(j, UNIT_SEPARATOR);

  if (EEPROM.commit())
  {
    STAT = "CONNECTION_SUCCESS";
    count = 1;
    if (debug)
    {
      Serial.println("Data successfully saved in EEPROM");
    }
  }
  else
  {
    if (debug)
    {
      Serial.println("ERROR : Data commit failed");
    }
    count++;
    if (count >= 3)
    {

      STAT = "give up saving EEPROM";
      if (debug)
      {
        Serial.println("ERROR! Data commit failed");
      }
    }
  }
}

void read_EEPROM(bool debug)
{
  user_SSID = "";
  password = "";
  unsigned int i = SSID_EEPROM_INDEX;
  byte c = EEPROM.read(i);
  while (c != UNIT_SEPARATOR and i < EEPROM_ASSIGNMENT)
  {
    user_SSID += char(c);
    i++;
    c = EEPROM.read(i);
  }
  i++;
  c = EEPROM.read(i);
  while (c != UNIT_SEPARATOR and i < EEPROM_ASSIGNMENT)
  {
    password += char(c);
    i++;
    c = EEPROM.read(i);
  }
  if (user_SSID == "" and password == "")
  {
    STAT = "HOTSPOT_RUNNING";
  }
  else
  {
    STAT = "TRYING_CONNECTION";
  }

  if (debug)
  {
    Serial.println("id readed");
    Serial.println("  SSID : " + user_SSID);
    Serial.println("  password : " + password);
  }
}

// inutile ici
void read_EEPROMbis(bool debug)
{
  unsigned int i = 0;
  while (i < EEPROM_ASSIGNMENT)
  {
    byte c = EEPROM.read(i);
    Serial.println(c);
    i++;
  }
}

unsigned long t0;
String Prev_STAT;

void configure_WiFi(bool debug)
{
  delay(1);
  if (Prev_STAT != STAT)
  {
    if (debug)
    {
      Serial.println();
      Serial.println("______________");
      Serial.println(STAT);
      Serial.println("______________");
      Serial.println();
    }
    Prev_STAT = STAT;
  }

  if (STAT == "INIT_CONFIGURING_WIFI")
  {
    t0 = millis();
    if (debug)
    {
      Serial.println("beginning of timeout counter at t = " + String(t0) + "ms");
      Serial.println(String(configure_WiFi_TIMEOUT / 1000) + "s remaining to configure the WiFi connection");
    }
    STAT = "READING_EEPROM";
  }
  else if (STAT == "READING_EEPROM")
  {
    read_EEPROM(debug);
  }
  else if (STAT == "TRYING_CONNECTION")
  {
    wifi_try_connection(debug);
  }
  else if (STAT == "CONNECTION_TIMEOUT")
  {
    SSID_received = false;
    password_received = false;
    STAT = "HOTSPOT_RUNNING";
  }
  else if (STAT == "HOTSPOT_RUNNING")
  {
    hot_spot_begin(debug);
  }
  else if (STAT == "TRYING_CONNECTION_SUCCESS")
  {
    write_EEPROM(debug);
    STAT = "CONNECTION_SUCCESS";
  }

  if (millis() - t0 >= configure_WiFi_TIMEOUT)
  {
    STAT = "configure_WiFi_TIMEOUT";
    WiFi.mode(WIFI_OFF);
    if (debug)
    {
      Serial.println();
      Serial.println("______________");
      Serial.println(STAT);
      Serial.println("______________");
      Serial.println();
      Serial.println("WiFi turned off");
    }
  }
}
