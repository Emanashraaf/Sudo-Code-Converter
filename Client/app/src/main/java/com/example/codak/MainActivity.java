package com.example.codak;

import android.Manifest;
import android.content.ContentResolver;
import android.content.ContentValues;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.database.Cursor;
import android.net.Uri;
import android.os.Build;
import android.os.Environment;
import android.provider.MediaStore;
import android.support.annotation.NonNull;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.Toast;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.net.Socket;

import id.zelory.compressor.Compressor;

public class MainActivity extends AppCompatActivity
{
    private static final int PERMISSION_CODE = 1000;
    private static final int IMAGE_CAPTURE_CODE = 1001;
    Button mCaptureBtn;
    Uri image_uri;
    byte[] image_buffer = new byte[1024];
    FileInputStream fis = null;
    public static String outputfile_path;

    public static Socket client= null;
    public static FileOutputStream fos = null;
    public static DataOutputStream dos = null;
    public static DataInputStream dis = null;

    @Override
    protected void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        mCaptureBtn = findViewById(R.id.upload_image);
        //button click
        mCaptureBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                //if system os is >= marshmallow, request runtime permission
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M){
                    if (checkSelfPermission(Manifest.permission.CAMERA) ==
                            PackageManager.PERMISSION_DENIED ||
                            checkSelfPermission(Manifest.permission.WRITE_EXTERNAL_STORAGE) ==
                                    PackageManager.PERMISSION_DENIED){
                        //permission not enabled, request it
                        String[] permission = {Manifest.permission.CAMERA, Manifest.permission.WRITE_EXTERNAL_STORAGE};
                        //show popup to request permissions
                        requestPermissions(permission, PERMISSION_CODE);
                    }
                    else {
                        //permission already granted
                        openCamera();
                    }
                }
                else {
                    //system os < marshmallow
                    openCamera();
                }
            }
        });
    }

    private void openCamera() {
        ContentValues values = new ContentValues();
        values.put(MediaStore.Images.Media.TITLE, "New Picture");
        values.put(MediaStore.Images.Media.DESCRIPTION, "From the Camera");
        image_uri = getContentResolver().insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, values);
        //Camera intent
        Intent cameraIntent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
        cameraIntent.putExtra(MediaStore.EXTRA_OUTPUT, image_uri);
        startActivityForResult(cameraIntent, IMAGE_CAPTURE_CODE);
    }

    // handling permission result
    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        //this method is called, when user presses Allow or Deny from Permission Request Popup
        switch (requestCode){
            case PERMISSION_CODE:{
                if (grantResults.length > 0 && grantResults[0] ==
                        PackageManager.PERMISSION_GRANTED){
                    //permission from popup was granted
                    openCamera();
                }
                else {
                    //permission from popup was denied
                    Toast.makeText(this, "Permission denied...", Toast.LENGTH_SHORT).show();
                }
            }
        }
    }

    public static String getFilePath(Context ctx, Uri uri)
    {
        ContentResolver cr = ctx.getContentResolver();
        String file_path = null;
        Cursor cursor = cr.query(uri,
                new String[] { android.provider.MediaStore.MediaColumns.DATA },
                null, null, null);
        if (cursor != null) {
            cursor.moveToFirst();
            file_path = cursor.getString(0);
            cursor.close();
        } else {
            file_path = uri.getPath();
        }
        return file_path;
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        //called when image was captured from camera

        if (resultCode == RESULT_OK)
        {
            thread.start();
        }
    }

    Thread thread = new Thread(new Runnable()
    {
        @Override
        public void run() {
            try {
                String ServerIP = "192.168.1.5";
                int PortNumber = 12345;

                // Connection with server
                Socket client = null;
                client = new Socket(ServerIP, PortNumber);
                dos = new DataOutputStream(client.getOutputStream());
                dis = new DataInputStream(client.getInputStream());

                // Read image
                String file_path = getFilePath(getBaseContext(), image_uri);
                File image = new File(file_path);
                File compressedImageFile = new Compressor(getBaseContext()).compressToFile(image);
                FileInputStream fis = new FileInputStream(compressedImageFile);

                // Send image to server
                while (fis.read(image_buffer) != -1) {
                    dos.write(image_buffer);
                }
                byte[] end = "done".getBytes();
                dos.write(end);

                // Receive output from server
                outputfile_path = Environment.getExternalStorageDirectory()+"/output.txt";
                File output = new File (outputfile_path);
                fos = new FileOutputStream(output);
                byte[] buffer = new byte[4096];
                dis.read(buffer);
                fos.write(buffer);
                fos.flush();
                fos.close();

                Intent intent = new Intent(getBaseContext(), view_output.class);
                startActivity(intent);

            }

            catch (Exception e)
            {
                    e.printStackTrace();
                }
            }
        });
}
