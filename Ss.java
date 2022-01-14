// nc 127.0.0.1 8080

package eu.j45.sock5;
import java.io.*;
import java.net.*;
import java.util.Date;

/**
 * Hello world!
 */
public final class Ss {
    private Ss() {
    }

    /**
     * Says hello to the world.
     * @param args The arguments of the program.
     */
    public static void main(String[] args) {

        int port = Integer.parseInt("8080");
 
        try (ServerSocket serverSocket = new ServerSocket(port)) {
 
            System.out.println("Server is listening on port " + port);
 
            while (true) {
                Socket socket = serverSocket.accept();
 
                System.out.println("New client connected");
 
                OutputStream output = socket.getOutputStream();
                PrintWriter writer = new PrintWriter(output, true);
 
                writer.println(new Date().toString());
            }
 
        } catch (IOException ex) {
            System.out.println("Server exception: " + ex.getMessage());
            ex.printStackTrace();
        }
    }
}





