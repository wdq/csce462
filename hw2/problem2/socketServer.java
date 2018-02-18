// NOTE: Save the code in a file named socketServer.java
import java.net.*;
import java.io.*;

public class socketServer extends Thread {
   private ServerSocket serverSocket;
   
   public socketServer() throws IOException {
      serverSocket = new ServerSocket(8080);
      serverSocket.setSoTimeout(10000);
   }

   public void run() {
      while(true) {
         try {
            System.out.println("Waiting for client on port " + 
               serverSocket.getLocalPort() + "...");
            Socket server = serverSocket.accept();
            
            System.out.println("Just connected to " + server.getRemoteSocketAddress());
            DataInputStream in = new DataInputStream(server.getInputStream());
            
            System.out.println(in.readUTF());
            DataOutputStream out = new DataOutputStream(server.getOutputStream());
            out.writeUTF("Thank you for connecting to " + server.getLocalSocketAddress()
               + "\nGoodbye!");
            server.close();
            
         } catch (SocketTimeoutException s) {
            System.out.println("Socket timed out!");
            break;
         } catch (IOException e) {
            e.printStackTrace();
            break;
         }
      }
   }
   
   public static void main(String [] args) {
      try {
         Thread t = new socketServer();
         t.start();
      } catch (IOException e) {
         e.printStackTrace();
      }
   }
}
