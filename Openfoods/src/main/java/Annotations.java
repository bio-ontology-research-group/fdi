import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.net.URLEncoder;
import uk.ac.ebi.chebi.webapps.chebiWS.client.ChebiWebServiceClient;
import uk.ac.ebi.chebi.webapps.chebiWS.model.ChebiWebServiceFault_Exception;
import uk.ac.ebi.chebi.webapps.chebiWS.model.*;


import org.apache.http.HttpEntity;
import org.apache.http.NameValuePair;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.message.BasicNameValuePair;
import org.apache.http.util.EntityUtils;

import com.google.gson.*;
import com.google.gson.stream.*;

public class Annotations {

    Properties props;

    public Annotations(Properties props) {
        this.props = props;
    }

    public void getChebiAnnotations() throws Exception {
        ChebiWebServiceClient client = new ChebiWebServiceClient();
        String filePath = "data/ingrs.txt";
        Map<String, List<LiteEntity> > mem = new HashMap<String, List<LiteEntity> >();
        PrintWriter out = new PrintWriter(new BufferedWriter(
            new FileWriter("data/ingrs-chebi.txt"), 1073741824));
        try(BufferedReader br = Files.newBufferedReader(Paths.get(filePath))) {
            String line;
            int c = 0;
            while((line = br.readLine()) != null) {
                // String[] items = line.split("\t", -1);
                // String query = items[2].trim();
                String query = line;
                List<LiteEntity> resultList = null;
                if (!mem.containsKey(query)) {
                    try {
                        LiteEntityList entities = client.getLiteEntity(
                            query,
                            SearchCategory.ALL,
                            5,
                            StarsCategory.ALL);
                        resultList = entities.getListElement();
                        mem.put(query, resultList);
                    } catch(Exception e) {
                        System.out.println(e.getMessage());
                        System.out.println(query + " " + query.length());
                        resultList = new ArrayList<LiteEntity>();
                    }
                } else {
                    resultList = mem.get(query);
                }
                for(LiteEntity entity: resultList) {
                    out.println(
                        line + "\t" + entity.getChebiId() + "|" +
                        entity.getChebiAsciiName() + "|" + entity.getSearchScore());
                }
            }
        }
        out.close();
    }

    public void getPubchemAnnotations() throws Exception {
        CloseableHttpClient httpclient = HttpClients.createDefault();
        try {
            String filePath = "data/ingrs.txt";
            Map<String, List<String> > mem = new HashMap<String, List<String> >();
            PrintWriter out = new PrintWriter(new BufferedWriter(
                new FileWriter("data/ingrs-pubchem.txt"), 1073741824));
            try(BufferedReader br = Files.newBufferedReader(Paths.get(filePath))) {
                String line;
                int c = 0;
                Gson gson = new Gson();
                while((line = br.readLine()) != null) {
                    String[] items = line.split("\t", -1);
                    String query = items[0].trim();
                    List<String> resultList = new ArrayList<String>();
                    if (!mem.containsKey(query)) {
                        String url = URLEncoder.encode("[display(cmpdname,cid)].from(pccompound_main).usingschema(/schema/pccompound_main).matching(text==\"" + query + "\").start(0).limit(20)", "UTF-8");
                        HttpGet httpGet = new HttpGet("https://pubchem.ncbi.nlm.nih.gov/ngram?q=" + url);
                        CloseableHttpResponse response = httpclient.execute(httpGet);
                        try {
                            HttpEntity entity = response.getEntity();
                            InputStream is = entity.getContent();
                            JsonReader reader = new JsonReader(new InputStreamReader(is, "UTF-8"));
                            JsonObject obj = new JsonParser().parse(reader).getAsJsonObject();
                            JsonArray content = obj.getAsJsonObject("ngout").getAsJsonObject("data").getAsJsonArray("content");
                            for (JsonElement elem: content) {
                                String cid = elem.getAsJsonObject().get("cid").getAsString();
                                String name = "";
                                if (elem.getAsJsonObject().has("cmpdname")) {
                                    name = elem.getAsJsonObject().get("cmpdname").getAsString();
                                }
                                resultList.add(cid + "|" + name);
                            }
                            // EntityUtils.consume(entity);
                        } finally {
                            response.close();
                        }
                        mem.put(query, resultList);
                    } else {
                        resultList = mem.get(query);
                    }
                    for(String entity: resultList) {
                        out.println(
                            line + "\t" + entity);
                    }
                    System.out.println(line + " - " + resultList.size());
                    Thread.sleep(100);
                }
            }
            out.close();
        } finally {
            httpclient.close();
        }

    }

    public void getDrugbankAnnotations() throws Exception {
        String filePath = "data/drug_links.csv";
        Map<String, Set<String> > map = new HashMap<String, Set<String> >();
        try(BufferedReader br = Files.newBufferedReader(Paths.get(filePath))) {
            String line = br.readLine();
            int c = 0;
            while((line = br.readLine()) != null) {
                String[] items = line.split(",", -1);
                String drugBankId = items[0].trim();
                String chebiId = items[8].trim();
                if (!chebiId.equals("") && !chebiId.equals("\"\"")) {
                    if(!map.containsKey(chebiId)) {
                        map.put(chebiId, new HashSet<String>());
                    }
                    map.get(chebiId).add(drugBankId);
                }
            }
        }


        // PrintWriter outChDb = new PrintWriter(new BufferedWriter(
        //     new FileWriter("data/chebi-drugbank.txt"), 1073741824));
        // for (String chebiId: map.keySet()) {
        //     Set<String> dbIds = map.get(chebiId);
        //     outChDb.print("CHEBI:" + chebiId);
        //     for (String dbId: dbIds) {
        //         outChDb.print(" " + dbId);
        //     }
        //     outChDb.println();
        // }
        // outChDb.close();


        filePath = "data/pubchem_drugbank_chebi.tsv";
        try(BufferedReader br = Files.newBufferedReader(Paths.get(filePath))) {
            String line;
            int c = 0;
            while((line = br.readLine()) != null) {
                String[] items = line.split("\t", -1);
                String drugBankIds = items[1].trim();
                String chebiIds = items[2].trim();
                if (!chebiIds.equals(".")) {
                    String[] chId = chebiIds.split("\\|");
                    String[] dbId = drugBankIds.split("\\|");
                    for (String chebiId: chId) {
                        chebiId = chebiId.split("\\:")[1];
                        for (String drugBankId: dbId) {
                            if(!map.containsKey(chebiId)) {
                                map.put(chebiId, new HashSet<String>());
                            }
                            map.get(chebiId).add(drugBankId);
                        }
                    }

                }
            }
        }

        PrintWriter out = new PrintWriter(new BufferedWriter(
            new FileWriter("data/ingrs-chebi-drugbank.txt"), 1073741824));
        filePath = "data/ingrs-chebi.txt";
        try(BufferedReader br = Files.newBufferedReader(Paths.get(filePath))) {
            String line;
            int c = 0;
            while((line = br.readLine()) != null) {
                String[] items = line.split("\t", -1);
                String[] chebis = items[1].split("\\|");
                String chebiId = chebis[0].split("\\:")[1];
                System.out.println(chebiId);
                out.print(line + "\t");
                if (map.containsKey(chebiId) && map.get(chebiId).size() > 0) {
                    Set<String> dbIds = map.get(chebiId);
                    String[] dbIdArray = new String[dbIds.size()];
                    dbIds.toArray(dbIdArray);
                    out.print(dbIdArray[0]);
                    for (int i = 1; i < dbIdArray.length; i++) {
                        out.print("|" + dbIdArray[i]);
                    }
                } else {
                    out.print(".");
                }
                out.println();
            }
        }
        out.close();
    }

    public void getHighScoreDB() throws Exception {
        String filePath = "data/ingrs-chebi-drugbank.txt";
        PrintWriter out = new PrintWriter(new BufferedWriter(
            new FileWriter("data/ingrs-chebi-drugbank-highscore.txt"), 1073741824));
        try(BufferedReader br = Files.newBufferedReader(Paths.get(filePath))) {
            String line;
            int c = 0;
            Set<String> set = new HashSet<String>();
            while((line = br.readLine()) != null) {
                String[] items = line.split("\t", -1);
                if (!items[2].equals(".") && !items[2].equals("")){
                    String[] chebis = items[1].split("\\|");
                    String chebiId = chebis[0];
                    String id = items[0] + "_" + items[2] + "_" + chebiId;
                    if (!set.contains(id)){
                        double score = Double.parseDouble(chebis[2]);
                        if (score > 0.01){
                            out.println(line + "\t");
                        }
                        set.add(id);
                    }
                }
            }
        }
        out.close();
    }

    public void mapPubchemDB() throws Exception {
        String filePath = "data/pubchem_drugbank_chebi.tsv";
        Map<String, String> map = new HashMap<String, String>();
        try(BufferedReader br = Files.newBufferedReader(Paths.get(filePath))) {
            String line;
            int c = 0;
            while((line = br.readLine()) != null) {
                String[] items = line.split("\t", -1);
                String pId = items[0];
                String dbId = items[1];
                // System.out.println(pId + " " + dbId);
                map.put(pId, dbId);
            }
        }
        PrintWriter out = new PrintWriter("data/pubchem-ingrs_DB.txt");
        filePath = "data/pubchem-ingrs.txt";
        try(BufferedReader br = Files.newBufferedReader(Paths.get(filePath))) {
            String line;
            int c = 0;
            while((line = br.readLine()) != null) {
                String[] items = line.split("\\|", -1);
                String pId = items[0];
                System.out.println(pId);
                if (map.containsKey(pId)) {
                    out.println(line + "\t" + map.get(pId));
                }
            }
        }
        out.close();
    }

    public void foodDrugDrugInteractions() throws Exception {
        String filePath = "data/drug-drug-interactions.tsv";
        Map<String, List<String> > map = new HashMap<String, List<String> >();
        try(BufferedReader br = Files.newBufferedReader(Paths.get(filePath))) {
            String line;
            int c = 0;
            while((line = br.readLine()) != null) {
                String[] items = line.split("\t", -1);
                String d1 = items[0];
                String d2 = items[1];
                if (!map.containsKey(d1)) {
                    map.put(d1, new ArrayList<String>());
                }
                map.get(d1).add(d2 + "\t" + items[2] + "\t" + items[3]);
            }
        }
        PrintWriter out = new PrintWriter("data/allfood-drug-drug-interactions.txt");
        filePath = "data/food-drugs-uniq.txt";
        try(BufferedReader br = Files.newBufferedReader(Paths.get(filePath))) {
            String line;
            int c = 0;
            while((line = br.readLine()) != null) {
                String[] items = line.split("\\|", -1);
                for (int i = 0; i < items.length; i++) {
                    if (map.containsKey(items[i])) {
                        for (String s: map.get(items[i])) {
                            out.println(items[i] + "\t" + s);
                        }
                    }
                }
            }
        }
        out.close();
    }

    public void validation() throws Exception {
        String filePath = "data/inter-drugs2.txt";
        Set<String> set = new HashSet<String>();
        try(BufferedReader br = Files.newBufferedReader(Paths.get(filePath))) {
            String line;
            while((line = br.readLine()) != null) {
                String[] items = line.split("\t", -1);
                String d1 = items[0];
                set.add(d1);
            }
        }
        filePath = "data/inter-drugs.txt";
        int c = 0;
        try(BufferedReader br = Files.newBufferedReader(Paths.get(filePath))) {
            String line;
            while((line = br.readLine()) != null) {
                String[] items = line.split("\t", -1);
                if (set.contains(items[0])){
                    c++;
                }
            }
        }
        System.out.println(c);
    }
}
