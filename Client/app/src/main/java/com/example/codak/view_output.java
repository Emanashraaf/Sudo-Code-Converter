package com.example.codak;

import android.annotation.SuppressLint;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.LinearLayout.LayoutParams;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.Scanner;

public class view_output extends AppCompatActivity
{
    TextView code , output;
    LinearLayout ll;
    LayoutParams lp;

    @Override
    protected void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_view_output);
        code = (TextView) findViewById(R.id.code);
        output = (TextView) findViewById(R.id.output);
        File file = new File(CodakActivity.outputfile_path);
        try
        {
            code.setText(new Scanner(file).useDelimiter("\\Z").next());
        }
        catch (FileNotFoundException e)
        {
            e.printStackTrace();
        }
    }

    Thread thread = new Thread(new Runnable()
    {
        @Override
        public void run() {
            try {
                ll = (LinearLayout) findViewById(R.id.ll);
                final LayoutParams lp = new LinearLayout.LayoutParams(
                        LayoutParams.WRAP_CONTENT, // Width of TextView
                        LayoutParams.WRAP_CONTENT); // Height of TextView
                lp.setMargins(10,10,10,10);

                CodakActivity.dos.write("run".getBytes());
                byte[] in_b = new byte[500];
                String in;

                int size = CodakActivity.dis.read(in_b);
                in = new String(in_b, 0, size, "UTF-8");
                CodakActivity.dos.write("-1".getBytes());

                while (!in.equals("end")) {
                    final String finalIn = in;
                    Log.w("Tag",finalIn);
                    runOnUiThread(new Runnable() {
                        @SuppressLint("ResourceAsColor")
                        public void run() {
                            if (finalIn.equals("input"))
                            {
                                final EditText et = new EditText(getBaseContext());
                                et.setLayoutParams(lp);
                                et.setTextSize(15f);
                                et.setTextColor(R.color.silver);
                                et.setBackgroundResource(R.color.white);
                                et.setSelection(0);
                                et.setHint("Enter input");
                                ll.addView(et);


                                Button ok = new Button(getBaseContext());
                                ok.setLayoutParams(lp);
                                ok.setText("Send");
                                ok.setTextSize(15f);
                                ok.setTextColor(Color.WHITE);
                                ok.setBackgroundResource(R.color.ko7ly);
                                ll.addView(ok);
                                ok.setOnClickListener(new View.OnClickListener() {
                                    public void onClick(View v) {
                                        String input = et.getText().toString();
                                        try {
                                            CodakActivity.dos.write(input.getBytes());
                                        } catch (IOException e) {
                                            e.printStackTrace();
                                        }
                                    }
                                });

                            }
                            else
                                {
                                TextView tv = new TextView(getBaseContext());
                                tv.setLayoutParams(lp);
                                tv.setTextSize(15f);
                                tv.setTextColor(R.color.silver);
                                tv.setText(finalIn);
                                ll.addView(tv);
                            }
                        }
                    });

                    in_b = new byte[500];
                    size = CodakActivity.dis.read(in_b);
                    in = new String(in_b, 0, size, "UTF-8");
                    CodakActivity.dos.write("-1".getBytes());
                }
                CodakActivity.client.close();
            }

            catch (Exception e)
            {
                e.printStackTrace();
            }
        }
    });

    public void execute(View v)
    {
        output.setVisibility(View.VISIBLE);
        thread.start();
    }
}
