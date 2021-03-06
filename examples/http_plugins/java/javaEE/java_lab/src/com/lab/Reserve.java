package com.lab;

import java.io.IOException;
import java.util.UUID;

import javax.servlet.ServletContext;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

import org.json.*;

import util.InfoReservation;




public class Reserve extends LabBase {

// For use reserve put this url in browser
// http://localhost:8080/java_lab/reserve/?username=jsmith&system_login=myplugin&system_password=password&back_url=http://www.google.com/
	/**
	 * 
	 */
	private static final long serialVersionUID = -8196377190923725493L;

	@Override
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		String systemLogin = request.getParameter("system_login");
		String systemPassword = request.getParameter("system_password");
		String username = request.getParameter("username");
		String backUrl = request.getParameter("back_url");
		JSONObject myJson = new JSONObject();
		if (systemLogin != null && systemPassword != null){
			if (systemLogin.equals(SYSTEM_LOGIN) && systemPassword.equals(SYSTEM_PASSWORD)){
				long now = System.currentTimeMillis();
				String reservationId = UUID.randomUUID().toString();
				ServletContext context = request.getServletContext();
				InfoReservation info = new InfoReservation(now + SESSION_SECONDS*1000,backUrl,username);
				context.setAttribute(reservationId,info);
				myJson.put("load_url","http://" + request.getServerName()  +":" + request.getServerPort() + request.getContextPath() + "/lab/" + "?reservation_id=" + reservationId);
				myJson.put("reservation_id", reservationId);
				response.getWriter().write(myJson.toString());
			}		
		}else{ 
			myJson.put("Error", "invalid credentials'");
			response.getWriter().write(myJson.toString());
		}
	}
}

