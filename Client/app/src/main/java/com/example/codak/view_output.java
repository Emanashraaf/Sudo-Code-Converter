package com.example.codak;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.widget.TextView;
import java.io.File;
import java.io.FileNotFoundException;
import java.util.Scanner;

public class view_output extends AppCompatActivity {

    TextView code;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_view_output);
        code = (TextView) findViewById(R.id.code);
        File file = new File(MainActivity.outputfile_path);
        try {
            code.setText(new Scanner(file).useDelimiter("\\Z").next());
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        }
    }
}
