package eu.j45.sock5;

import java.net.*;
import java.util.Arrays;
import java.io.*;

public class S5S_Test {
 // initialize socket and input output streams
 private Socket socket = null;
 private OutputStream out = null;
 private InputStream in = null;

 // constructor to put ip address and port
 public S5S_Test(String address, int port) {
  // establish a connection
  try {
   socket = new Socket(address, port);
   if (socket.isConnected()) {
    System.out.println("Connected");
   }

   // sends output to the socket
   out = new DataOutputStream(socket.getOutputStream());
   //takes input from socket
   in = new DataInputStream(socket.getInputStream());
  } catch (UnknownHostException u) {
   System.out.println(u);
  } catch (IOException i) {
   System.out.println(i);
  }

  
  try {
   byte[] clientGreeting = {(byte)0x05, (byte)0x01, (byte)0x02};
   out.write(clientGreeting);

   String readableQuery = Arrays.toString(clientGreeting);
   //printing request to console
   System.out.println("Sent to server : " + readableQuery);

   // Receiving reply from server
   ByteArrayOutputStream baos = new ByteArrayOutputStream();
   byte buffer[] = new byte[3];
   baos.write(buffer, 0 , in.read(buffer));
   
   byte result[] = baos.toByteArray();

   String res = Arrays.toString(result);

   // printing reply to console
   System.out.println("Recieved from server : " + res);
  } catch (IOException i) {
   System.out.println(i);
  }
  // }

  // close the connection
  try {
   // input.close();
   in.close();
   out.close();
   socket.close();
  } catch (IOException i) {
   System.out.println(i);
  }
 }

 public static void main(String args[]) {
  new S5S_Test("127.0.0.1", 5000);
 }
}


//byte[] message = {(byte)0x05, (byte)0x01, (byte)0x02}; // perso

