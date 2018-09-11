package com.amazonaws.example.fileserver.syncher.service;

public interface DataSyncService {

	public void startPuller();
	public void startPusher();
	
	public void push();
	public void pull();
	
	
}
