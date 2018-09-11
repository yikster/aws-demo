package com.amazonaws.example.fileserver.repository;

import java.util.List;

import com.amazonaws.example.fileserver.model.FileInfo;

public interface DDBRepository {
	List<FileInfo> scan();
	List<FileInfo> getByGuid(String guid);
	void addNewFileRecord(FileInfo fileInfo);

}
