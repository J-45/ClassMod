package eu.j45.sock5;

import java.net.*;
import java.util.Arrays;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.Assert.assertEquals;
import java.io.*;

public class S5S_Test {
 // initialize socket and input output streams
 private Socket socket = null;
 private InputStream in = null;
 private OutputStream out = null;
 private String address = "127.0.0.1";
 private int port = 5000;
 private ByteArrayOutputStream baos = new ByteArrayOutputStream();

 // constructor to put ip address and port

  // establish a connection

  @BeforeEach
  void openSocket_Test() throws UnknownHostException, IOException {

	  this.socket = new Socket(this.address, this.port);
	   if (this.socket.isConnected()) {
//	    System.out.println("Connected");
	   }

	   // sends output to the socket
	   this.out = new DataOutputStream(this.socket.getOutputStream());
	   //takes input from socket
	   this.in = new DataInputStream(this.socket.getInputStream());
  }
  
  @Test
  @DisplayName("good greeting")
  void greeting_Test() throws IOException {
	   byte[] clientGreeting = {(byte)0x05, (byte)0x01, (byte)0x02};
	   String res = sendMessageToServer(clientGreeting);
	   String goodResp = "[5, 2]";
	   
	   assertEquals(goodResp, res);

  }
  
  @Test
  @DisplayName("bad greeting")
  void greeting2_Test() throws IOException {
	   byte[] clientGreeting = {(byte)0x05, (byte)0x01, (byte)0x03};
	   String res = sendMessageToServer(clientGreeting);
	   String goodResp = "[5, -1]";
	   
	   assertEquals(goodResp, res);

  }
  
  String sendMessageToServer(byte[] messageBytes) throws IOException {

	   this.out.write(messageBytes);

	   String readableQuery = Arrays.toString(messageBytes);
	   //printing request to console
	   // Sent to server :
	   System.out.println(">> " + readableQuery);

	   // Receiving reply from server
	   byte buffer[] = new byte[3];
	   this.baos.write(buffer, 0 , this.in.read(buffer));
	   byte result[] = this.baos.toByteArray();

	   String res = Arrays.toString(result);

	   // printing reply to console
	   // Recieved from server
	   System.out.println("<< " + res);
	   return res;
  }
  
  @AfterEach
  void closeSocket_Test() throws IOException {
	  // close the connection
	   this.in.close();
	   this.out.close();
	   this.socket.close();
//	   System.out.println("Deconnected");
  }

}
