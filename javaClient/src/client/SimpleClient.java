package client;

import java.net.InetAddress;
import java.net.UnknownHostException;

import com.datastax.driver.core.Cluster;
import com.datastax.driver.core.ResultSet;
import com.datastax.driver.core.Row;
import com.datastax.driver.core.Session;

public class SimpleClient {
	private Cluster cluster;

	public Session connect(InetAddress ... node) {
		cluster = Cluster.builder()
						.addContactPoints(node)
						.build();
		return cluster.connect("system");	
	}

	public void close() {
		cluster.shutdown();
	}

	public static void main(String[] args) throws UnknownHostException {
		System.out.println(InetAddress.getLocalHost());
		SimpleClient client = new SimpleClient();
		Session s = client.connect(InetAddress.getByAddress("group3@uofa391-instance-2",new byte[] {10,0,0,38}));
		s.getCluster();
		ResultSet rs = s.execute("SELECT keyspace_name, columnfamily_name FROM schema_columnfamilies");
		for(Row r : rs){
			System.out.println(r);
		}
		client.close();
		
	}
}