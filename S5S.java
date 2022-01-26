// nc 127.0.0.1 8080

package eu.j45.sock5;

import java.net.*;
import java.util.Arrays;
import java.io.*; 

public class S5S 
{ 
 //initialize socket and input stream 
 private Socket   socket = null; 
 private ServerSocket server = null; 
 private InputStream in  = null; 
 private OutputStream out = null;
 private ByteArrayOutputStream baos = new ByteArrayOutputStream();
 private int port = 5000;
 
 // constructor with port 
 public S5S(int port) throws IOException 
 { 
  // starts server and waits for a connection 

   this.server = new ServerSocket(this.port); 
   System.out.println("Server started"); 
   System.out.println("Waiting for a client ..."); 
   this.socket = server.accept(); 
   System.out.println("Client accepted"); 
   
   // takes input from the client socket 
   this.in = new DataInputStream(this.socket.getInputStream()); 
   //writes on client socket
   this.out = new DataOutputStream(this.socket.getOutputStream());
   
   while (greeting() != true) {
	   // code block to be executed
   }

   System.out.println("Closing connection"); 
   // close connection 
   this.socket.close(); 
   this.in.close(); 
   
 }
 
 public boolean greeting() throws IOException {
	 
	   // Receiving data from client

	   byte buffer[] = new byte[3];
	   this.baos.write(buffer, 0 , this.in.read(buffer));
	   byte result[] = this.baos.toByteArray();
	   
	   String readableRespond = Arrays.toString(result);
	   System.out.println("Recieved from client : "+readableRespond); 
	   
	   byte serverGreeting[] = new byte[]{5,2};
	   
	   //echoing back to client
	   if (Arrays.equals(result, new byte[] {5,1,2}) ) {
		   this.out.write(serverGreeting);
		   return true;
	   }else {
		   this.out.write(result);
		   return false;
	   }
 }

 public static void main(String args[]) throws IOException 
 { 
  new S5S(5000); 
 } 
}
