// nc 127.0.0.1 8080

package eu.j45.sock5;

import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.Arrays;

public class S5S {

   public static void main(String args[]) throws IOException {

       ServerSocket listener = null;

       System.out.println("Server is waiting to accept user...");
       int clientNumber = 0;

       // Try to open a server socket on port 7777
       // Note that we can't choose a port less than 1023 if we are not
       // privileged users (root)

       try {
           listener = new ServerSocket(5000);
       } catch (IOException e) {
           System.out.println(e);
           System.exit(1);
       }

       try {
           while (true) {
               // Accept client connection request
               // Get new Socket at Server.

               Socket socketOfServer = listener.accept();
               new ServiceThread(socketOfServer, clientNumber++).start();
           }
       } finally {
           listener.close();
       }

   }

   private static void log(String message) {
       System.out.println(message);
   }

   private static class ServiceThread extends Thread {

       private int clientNumber;
       private Socket socketOfServer;

       public ServiceThread(Socket socketOfServer, int clientNumber) {
           this.clientNumber = clientNumber;
           this.socketOfServer = socketOfServer;

           // Log
           log("New connection with client# " + this.clientNumber + " at " + socketOfServer);
       }

       @Override
       public void run() {

           try {

               // Open input and output streams
               DataInputStream is = new DataInputStream(socketOfServer.getInputStream());
               DataOutputStream os = new DataOutputStream(socketOfServer.getOutputStream());

               while (true) {
                   // Read data to the server (sent from client).
                   
                   
                   byte buffer[] = new byte[3];
                   ByteArrayOutputStream baos = new ByteArrayOutputStream();
            	   baos.write(buffer, 0 , is.read(buffer));
            	   byte result[] = baos.toByteArray();
            	   
            	   String readableRespond = Arrays.toString(result);
            	   System.out.println("Recieved from client : "+readableRespond); 
            	   
            	   byte serverGreeting[] = new byte[]{5,2};
            	   byte serverEndingCom[] = new byte[]{5,(byte)0xFF};
            	   
                   
                   // Write to socket of Server

                   if (Arrays.equals(result, new byte[] {5,1,2})) {
                       os.write(serverGreeting);
//                       os.flush();
                       break;
                   }else {
                	   os.write(serverEndingCom);
//                     os.flush();
                	   break;
                   }
               }

           } catch (IOException e) {
               System.out.println(e);
               e.printStackTrace();
           }
       }
   }
}
